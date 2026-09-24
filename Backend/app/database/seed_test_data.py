import hashlib
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "db.db"


def report_hash(report_code: str) -> str:
    return hashlib.sha256(f"AgriTrace PDF content: {report_code}".encode()).hexdigest()


def audit_trail(conn, user_id, action, entity_type, entity_id, created_at, old=None, new=None):
    conn.execute(
        """
        INSERT INTO audit_trails
            (user_id, action, entity_type, entity_id, old_value, new_value, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            action,
            entity_type,
            entity_id,
            json.dumps(old, ensure_ascii=False) if old is not None else None,
            json.dumps(new, ensure_ascii=False) if new is not None else None,
            created_at,
        ),
    )


def reset_seed_data(conn):
    for table in ("integrity_proofs", "trace_records", "packages", "audit_trails", "lab_reports", "samples", "batches", "businesses"):
        conn.execute(f"DELETE FROM {table}")


def seed_test_data():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        farmers = conn.execute("SELECT id, full_name FROM users WHERE role = 'FARMER' ORDER BY id").fetchall()
        auditors = conn.execute("SELECT id, full_name FROM users WHERE role = 'AUDITOR' ORDER BY id").fetchall()
        if len(farmers) < 2 or len(auditors) < 2:
            raise RuntimeError("Cần ít nhất 2 FARMER và 2 AUDITOR. Hãy chạy initialize_database() trước.")

        reset_seed_data(conn)
        farmer_1, farmer_2 = farmers[:2]
        auditor_1, auditor_2 = auditors[:2]

        conn.executemany(
            "INSERT INTO businesses (user_id, business_name, business_type, product_type, tax_code) VALUES (?, ?, ?, ?, ?)",
            [
                (farmer_1[0], "Hợp tác xã Nông nghiệp Xanh", "Hợp tác xã", "Rau quả", "0101234567"),
                (farmer_2[0], "Trang trại Green Farm", "Trang trại", "Rau quả", "0107654321"),
            ],
        )

        batch_specs = [
            ("001", "Dưa lưới", "Hà Nội", 500, "2026-08-23", "2026-09-15", "UNVERIFIED", farmer_1),
            ("002", "Cà chua bi", "Hà Nội", 300, "2026-08-24", "2026-09-10", "UNVERIFIED", farmer_2),
            ("003", "Dưa chuột", "Hà Nội", 450, "2026-08-25", "2026-09-12", "UNVERIFIED", farmer_1),
            ("004", "Gạo ST25", "Nam Định", 1000, "2026-08-20", "2027-08-20", "AUDITED", farmer_2),
            ("005", "Rau cải xanh", "Hà Nội", 250, "2026-08-26", "2026-09-05", "REJECTED", farmer_2),
            ("006", "Cam Cao Phong", "Hòa Bình", 800, "2026-08-18", "2026-10-18", "AUDITED", farmer_1),
            ("007", "Dưa lưới vàng", "Hà Nội", 600, "2026-08-27", "2026-09-20", "UNVERIFIED", farmer_1),
            ("008", "Xoài cát", "Tiền Giang", 700, "2026-08-15", "2026-09-30", "REJECTED", farmer_2),
            ("009", "Rau xà lách", "Hà Nội", 150, "2026-08-28", "2026-09-07", "UNVERIFIED", farmer_2),
            ("010", "Bưởi Diễn", "Hà Nội", 900, "2026-08-10", "2026-11-10", "AUDITED", farmer_1),
        ]

        batch_ids = {}
        for code, product, origin, quantity, production_date, expiry_date, status, farmer in batch_specs:
            batch_code = f"BATCH-HN-2026-{code}"
            cur = conn.execute(
                """
                INSERT INTO batches
                    (batch_code, product_name, producer_name, origin, quantity, unit,
                     production_date, expiry_date, status, farmer_id, created_at)
                VALUES (?, ?, ?, ?, ?, 'kg', ?, ?, ?, ?, ?)
                """,
                (batch_code, product, farmer[1], origin, quantity, production_date, expiry_date, status, farmer[0], f"2026-08-{10 + int(code):02d} 08:00:00"),
            )
            batch_ids[code] = cur.lastrowid
            audit_trail(conn, farmer[0], "CREATE_BATCH", "batch", cur.lastrowid, f"2026-08-{10 + int(code):02d} 08:00:00", new={"batch_code": batch_code, "status": "UNVERIFIED", "farmer_id": farmer[0]})

        sample_specs = {
            "001": ("PENDING", "2026-08-25", "Hà Nội"),
            "002": ("PENDING", "2026-08-26", "Hà Nội"),
            "004": ("APPROVED", "2026-08-22", "Nam Định"),
            "005": ("REJECTED", "2026-08-27", "Hà Nội"),
            "006": ("APPROVED", "2026-08-20", "Hòa Bình"),
            "007": ("PENDING", "2026-08-28", "Hà Nội"),
            "008": ("REJECTED", "2026-08-17", "Tiền Giang"),
            "009": ("PENDING", "2026-08-29", "Hà Nội"),
            "010": ("APPROVED", "2026-08-12", "Hà Nội"),
        }
        sample_ids = {}
        for code, (status, sampling_date, location) in sample_specs.items():
            sample_code = f"SMP-HN-2026-{code}"
            cur = conn.execute(
                """
                INSERT INTO samples
                    (sample_code, batch_id, sampling_date, sample_quantity, sample_unit,
                     sampling_location, sampling_method, status, created_at)
                VALUES (?, ?, ?, 0.5, 'kg', ?, 'Random sampling', ?, ?)
                """,
                (sample_code, batch_ids[code], sampling_date, location, status, sampling_date + " 09:00:00"),
            )
            sample_ids[code] = cur.lastrowid
            audit_trail(conn, auditor_1[0], "CREATE_SAMPLE", "sample", cur.lastrowid, sampling_date + " 10:00:00", new={"batch_id": batch_ids[code], "sample_code": sample_code, "status": status})

        uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        for old_file in uploads_dir.glob("seed_lab_report_*.pdf"):
            old_file.unlink()

        report_specs = {
            "004": ("PASS", "APPROVED", auditor_1, "2026-08-24", "2026-08-26"),
            "005": ("FAIL", "REJECTED", auditor_1, "2026-08-29", "2026-09-01"),
            "006": ("PASS", "APPROVED", auditor_2, "2026-08-22", "2026-08-25"),
            "007": ("PASS", "PENDING", auditor_2, "2026-08-30", None),
            "008": ("FAIL", "REJECTED", auditor_2, "2026-08-20", "2026-08-23"),
            "010": ("PASS", "APPROVED", auditor_1, "2026-08-15", "2026-08-18"),
        }
        for code, (result, status, uploader, report_date, _) in report_specs.items():
            report_code = f"LTR-HN-2026-{code}"
            file_name = f"seed_lab_report_{code}.pdf"
            file_bytes = f"%PDF-1.4\nAgriTrace seed laboratory report {report_code}\n%%EOF\n".encode()
            (uploads_dir / file_name).write_bytes(file_bytes)
            file_hash = hashlib.sha256(file_bytes).hexdigest()
            cur = conn.execute(
                """
                INSERT INTO lab_reports
                    (report_code, sample_id, batch_id, lab_name, lab_code, report_date,
                     result, file_name, file_hash, file_path, status, created_at)
                VALUES (?, ?, ?, 'ABC Agricultural Testing Laboratory', 'LAB-ABC-001', ?, ?, ?, ?, ?, ?, ?)
                """,
                (report_code, sample_ids[code], batch_ids[code], report_date, result, file_name, file_hash, f"/uploads/{file_name}", status, report_date + " 14:00:00"),
            )
            previous_proof = conn.execute(
                "SELECT proof_hash FROM integrity_proofs ORDER BY id DESC LIMIT 1"
            ).fetchone()
            previous_proof = previous_proof[0] if previous_proof else ""
            proof_hash = hashlib.sha256(
                f"{previous_proof}:{cur.lastrowid}:{batch_ids[code]}:{file_hash}".encode()
            ).hexdigest()
            conn.execute(
                "INSERT INTO integrity_proofs (report_id, batch_id, file_hash, previous_proof, proof_hash) VALUES (?, ?, ?, ?, ?)",
                (cur.lastrowid, batch_ids[code], file_hash, previous_proof or None, proof_hash),
            )
            audit_trail(conn, uploader[0], "UPLOAD_LAB_REPORT", "lab_report", cur.lastrowid, report_date + " 14:00:00", new={"report_code": report_code, "batch_id": batch_ids[code], "sample_id": sample_ids[code], "file_hash": file_hash, "status": status})

        audit_specs = {
            "004": (auditor_1, "2026-08-26 16:00:00", "All required documents and SHA-256 integrity check are valid.", "AUDITED"),
            "005": (auditor_1, "2026-09-01 16:00:00", "Laboratory result does not satisfy required quality criteria.", "REJECTED"),
            "006": (auditor_2, "2026-08-25 16:30:00", "Documents and SHA-256 integrity check passed.", "AUDITED"),
            "008": (auditor_2, "2026-08-23 15:30:00", "Invalid laboratory result. Farmer must correct and resubmit.", "REJECTED"),
            "010": (auditor_1, "2026-08-18 16:00:00", "All verification requirements passed.", "AUDITED"),
        }
        for code, (auditor, audit_date, reason, new_status) in audit_specs.items():
            audit_trail(conn, auditor[0], "APPROVE_BATCH" if new_status == "AUDITED" else "REJECT_BATCH", "batch", batch_ids[code], audit_date, old={"status": "UNVERIFIED"}, new={"status": new_status, "reason": reason, "auditor_id": auditor[0], "auditor_name": auditor[1]})

        for code in ("004", "006", "010"):
            package_code = f"PKG-HN-2026-{code}-001"
            trace_id = f"TRACE-HN-2026-{code}"
            cur = conn.execute(
                "INSERT INTO packages (package_code, batch_id, quantity, unit, qr_code, trace_id, status, created_at) VALUES (?, ?, 100, 'kg', ?, ?, 'ACTIVE', ?)",
                (package_code, batch_ids[code], f"QR-{code}", trace_id, audit_specs[code][1]),
            )
            conn.execute(
                "INSERT INTO trace_records (batch_id, package_id, trace_id, public_url, created_at) VALUES (?, ?, ?, ?, ?)",
                (batch_ids[code], cur.lastrowid, trace_id, f"/trace.html?trace_id={trace_id}", audit_specs[code][1]),
            )

        conn.commit()
        print("ĐÃ SEED TEST DATA NHẤT QUÁN")
        for row in conn.execute("SELECT batch_code, status, farmer_id FROM batches ORDER BY batch_code"):
            print(f"{row[0]} | {row[1]} | farmer_id={row[2]}")
    finally:
        conn.close()


if __name__ == "__main__":
    seed_test_data()
