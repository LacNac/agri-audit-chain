import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "db.db"


def seed_test_data():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # Get existing users from init_db.py
        farmers = conn.execute(
            "SELECT id, username, full_name FROM users WHERE role = 'FARMER' ORDER BY id"
        ).fetchall()

        auditors = conn.execute(
            "SELECT id, username, full_name FROM users WHERE role = 'AUDITOR' ORDER BY id"
        ).fetchall()

        if not farmers:
            raise RuntimeError("Chưa có FARMER. Hãy chạy initialize_database() trước.")

        if not auditors:
            raise RuntimeError("Chưa có AUDITOR. Hãy chạy initialize_database() trước.")

        farmer_1 = farmers[0]
        farmer_2 = farmers[1] if len(farmers) > 1 else farmers[0]
        auditor_1 = auditors[0]
        auditor_2 = auditors[1] if len(auditors) > 1 else auditors[0]

        # Avoid duplicate seed data when running the script repeatedly.
        batch_codes = [
            f"BATCH-HN-2026-{i:03d}" for i in range(1, 11)
        ]

        for code in batch_codes:
            conn.execute("DELETE FROM trace_records WHERE batch_id IN "
                         "(SELECT id FROM batches WHERE batch_code = ?)", (code,))
            conn.execute("DELETE FROM packages WHERE batch_id IN "
                         "(SELECT id FROM batches WHERE batch_code = ?)", (code,))
            conn.execute("DELETE FROM audit_logs WHERE batch_id IN "
                         "(SELECT id FROM batches WHERE batch_code = ?)", (code,))
            conn.execute("DELETE FROM lab_reports WHERE batch_id IN "
                         "(SELECT id FROM batches WHERE batch_code = ?)", (code,))
            conn.execute("DELETE FROM samples WHERE batch_id IN "
                         "(SELECT id FROM batches WHERE batch_code = ?)", (code,))
            conn.execute("DELETE FROM batches WHERE batch_code = ?", (code,))

        batches = [
            (
                "BATCH-HN-2026-001",
                "Dưa lưới",
                "Hợp tác xã Nông nghiệp Xanh",
                "Hà Nội",
                500,
                "kg",
                "2026-08-23",
                "2026-09-15",
                "UNVERIFIED",
                farmer_1[0],
            ),
            (
                "BATCH-HN-2026-002",
                "Cà chua bi",
                "Trang trại Green Farm",
                "Hà Nội",
                300,
                "kg",
                "2026-08-24",
                "2026-09-10",
                "UNVERIFIED",
                farmer_2[0],
            ),
            (
                "BATCH-HN-2026-003",
                "Dưa chuột",
                "Hợp tác xã Nông nghiệp Xanh",
                "Hà Nội",
                450,
                "kg",
                "2026-08-25",
                "2026-09-12",
                "UNVERIFIED",
                farmer_1[0],
            ),
            (
                "BATCH-HN-2026-004",
                "Gạo ST25",
                "HTX Nông nghiệp Đồng Bằng",
                "Nam Định",
                1000,
                "kg",
                "2026-08-20",
                "2027-08-20",
                "AUDITED",
                farmer_2[0],
            ),
            (
                "BATCH-HN-2026-005",
                "Rau cải xanh",
                "Trang trại Green Farm",
                "Hà Nội",
                250,
                "kg",
                "2026-08-26",
                "2026-09-05",
                "REJECTED",
                farmer_2[0],
            ),
            (
                "BATCH-HN-2026-006",
                "Cam Cao Phong",
                "HTX Cao Phong",
                "Hòa Bình",
                800,
                "kg",
                "2026-08-18",
                "2026-10-18",
                "AUDITED",
                farmer_1[0],
            ),
            (
                "BATCH-HN-2026-007",
                "Dưa lưới vàng",
                "Hợp tác xã Nông nghiệp Xanh",
                "Hà Nội",
                600,
                "kg",
                "2026-08-27",
                "2026-09-20",
                "UNVERIFIED",
                farmer_1[0],
            ),
            (
                "BATCH-HN-2026-008",
                "Xoài cát",
                "Trang trại Mekong",
                "Tiền Giang",
                700,
                "kg",
                "2026-08-15",
                "2026-09-30",
                "REJECTED",
                farmer_2[0],
            ),
            (
                "BATCH-HN-2026-009",
                "Rau xà lách",
                "Trang trại Green Farm",
                "Hà Nội",
                150,
                "kg",
                "2026-08-28",
                "2026-09-07",
                "UNVERIFIED",
                farmer_2[0],
            ),
            (
                "BATCH-HN-2026-010",
                "Bưởi Diễn",
                "HTX Nông nghiệp Đồng Bằng",
                "Hà Nội",
                900,
                "kg",
                "2026-08-10",
                "2026-11-10",
                "AUDITED",
                farmer_1[0],
            ),
        ]

        conn.executemany(
            """
            INSERT INTO batches
            (
                batch_code, product_name, producer_name, origin,
                quantity, unit, production_date, expiry_date,
                status, farmer_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            batches,
        )

        batch_rows = {
            row[1]: row[0]
            for row in conn.execute(
                "SELECT id, batch_code FROM batches WHERE batch_code LIKE 'BATCH-HN-2026-%'"
            ).fetchall()
        }

        # Samples:
        # 001: complete
        # 002: sample only, no report
        # 003: no sample
        # 004: complete
        # 005: complete, rejected
        # 006: complete, audited
        # 007: complete, report with hash
        # 008: complete, rejected
        # 009: sample only
        # 010: complete, audited
        samples = [
            ("SMP-HN-2026-001", batch_rows["BATCH-HN-2026-001"], "2026-08-25", 0.5, "kg", "Hà Nội", "Random sampling", "PENDING"),
            ("SMP-HN-2026-002", batch_rows["BATCH-HN-2026-002"], "2026-08-26", 0.5, "kg", "Hà Nội", "Random sampling", "PENDING"),
            ("SMP-HN-2026-004", batch_rows["BATCH-HN-2026-004"], "2026-08-22", 0.5, "kg", "Nam Định", "Random sampling", "APPROVED"),
            ("SMP-HN-2026-005", batch_rows["BATCH-HN-2026-005"], "2026-08-27", 0.5, "kg", "Hà Nội", "Random sampling", "REJECTED"),
            ("SMP-HN-2026-006", batch_rows["BATCH-HN-2026-006"], "2026-08-20", 0.5, "kg", "Hòa Bình", "Random sampling", "APPROVED"),
            ("SMP-HN-2026-007", batch_rows["BATCH-HN-2026-007"], "2026-08-28", 0.5, "kg", "Hà Nội", "Random sampling", "PENDING"),
            ("SMP-HN-2026-008", batch_rows["BATCH-HN-2026-008"], "2026-08-17", 0.5, "kg", "Tiền Giang", "Random sampling", "REJECTED"),
            ("SMP-HN-2026-009", batch_rows["BATCH-HN-2026-009"], "2026-08-29", 0.5, "kg", "Hà Nội", "Random sampling", "PENDING"),
            ("SMP-HN-2026-010", batch_rows["BATCH-HN-2026-010"], "2026-08-12", 0.5, "kg", "Hà Nội", "Random sampling", "APPROVED"),
        ]

        conn.executemany(
            """
            INSERT INTO samples
            (
                sample_code, batch_id, sampling_date, sample_quantity,
                sample_unit, sampling_location, sampling_method, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            samples,
        )

        sample_rows = {
            row[1]: row[0]
            for row in conn.execute(
                "SELECT id, sample_code FROM samples WHERE sample_code LIKE 'SMP-HN-2026-%'"
            ).fetchall()
        }

        # Laboratory reports
        reports = [
            (
                "LTR-HN-2026-001",
                sample_rows["SMP-HN-2026-001"],
                batch_rows["BATCH-HN-2026-001"],
                "ABC Agricultural Testing Laboratory",
                "LAB-ABC-001",
                "2026-08-28",
                "PASS",
                "report_batch_001.pdf",
                "8b7e8d2f5b6a9e0f5d2f2a0e7c1d4b6f9a3e5c8d7b2a1f0e4d6c9b8a7e5f2c1",
                "/reports/report_batch_001.pdf",
                "APPROVED",
            ),
            (
                "LTR-HN-2026-004",
                sample_rows["SMP-HN-2026-004"],
                batch_rows["BATCH-HN-2026-004"],
                "ABC Agricultural Testing Laboratory",
                "LAB-ABC-001",
                "2026-08-24",
                "PASS",
                "report_batch_004.pdf",
                "9a1c7e5f2b4d8a6e0f3c9b7d5e1a2f4c6b8d0e9f7a5c3b1d2e4f6a8c0b9d7e5",
                "/reports/report_batch_004.pdf",
                "APPROVED",
            ),
            (
                "LTR-HN-2026-005",
                sample_rows["SMP-HN-2026-005"],
                batch_rows["BATCH-HN-2026-005"],
                "ABC Agricultural Testing Laboratory",
                "LAB-ABC-001",
                "2026-08-29",
                "FAIL",
                "report_batch_005.pdf",
                "4c9e2a7b5d1f8e3c6a0b9d2f4e7c1a5b8d6f3e0c2a9b7d4f1e8c5a2b6d9f0e3",
                "/reports/report_batch_005.pdf",
                "REJECTED",
            ),
            (
                "LTR-HN-2026-006",
                sample_rows["SMP-HN-2026-006"],
                batch_rows["BATCH-HN-2026-006"],
                "ABC Agricultural Testing Laboratory",
                "LAB-ABC-001",
                "2026-08-22",
                "PASS",
                "report_batch_006.pdf",
                "a7f3c9e1b5d8a2f6c4e0b7d9f1a3c5e8b2d6f4a0c9e7b5d3f1a8c6e2b4d0f9",
                "/reports/report_batch_006.pdf",
                "APPROVED",
            ),
            (
                "LTR-HN-2026-007",
                sample_rows["SMP-HN-2026-007"],
                batch_rows["BATCH-HN-2026-007"],
                "ABC Agricultural Testing Laboratory",
                "LAB-ABC-001",
                "2026-08-30",
                "PASS",
                "report_batch_007.pdf",
                "c4e8a1f7b3d9e2c6a5f0b8d4e7a3c1f9b6d2e5a8c0f4b7d1e9a6c3f2b5d8e0",
                "/reports/report_batch_007.pdf",
                "PENDING",
            ),
            (
                "LTR-HN-2026-008",
                sample_rows["SMP-HN-2026-008"],
                batch_rows["BATCH-HN-2026-008"],
                "ABC Agricultural Testing Laboratory",
                "LAB-ABC-001",
                "2026-08-20",
                "FAIL",
                "report_batch_008.pdf",
                "e2a6c9f4b8d1e7a3c5f0b9d2e6a4c8f1b7d3e5a9c0f6b2d8e4a1c7f5b9d3e6",
                "/reports/report_batch_008.pdf",
                "REJECTED",
            ),
            (
                "LTR-HN-2026-010",
                sample_rows["SMP-HN-2026-010"],
                batch_rows["BATCH-HN-2026-010"],
                "ABC Agricultural Testing Laboratory",
                "LAB-ABC-001",
                "2026-08-15",
                "PASS",
                "report_batch_010.pdf",
                "f1c7a3e9b5d2f8a0c4e6b1d9a7f3c5e2b8d0a6f4c9e1b7d3a5f8c2e6b0d4a9",
                "/reports/report_batch_010.pdf",
                "APPROVED",
            ),
        ]

        conn.executemany(
            """
            INSERT INTO lab_reports
            (
                report_code, sample_id, batch_id, lab_name, lab_code,
                report_date, result, file_name, file_hash, file_path, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            reports,
        )

        # Audit history
        audit_data = [
            ("BATCH-HN-2026-004", auditor_1[0], "APPROVE", "UNVERIFIED", "AUDITED", "All required documents and integrity hash are valid."),
            ("BATCH-HN-2026-005", auditor_1[0], "REJECT", "UNVERIFIED", "REJECTED", "Laboratory result does not satisfy required quality criteria."),
            ("BATCH-HN-2026-006", auditor_2[0], "APPROVE", "UNVERIFIED", "AUDITED", "Documents and SHA-256 integrity check passed."),
            ("BATCH-HN-2026-008", auditor_2[0], "REJECT", "UNVERIFIED", "REJECTED", "Invalid laboratory result. Farmer must correct and resubmit."),
            ("BATCH-HN-2026-010", auditor_1[0], "APPROVE", "UNVERIFIED", "AUDITED", "All verification requirements passed."),
        ]

        for code, user_id, action, old_status, new_status, reason in audit_data:
            conn.execute(
                """
                INSERT INTO audit_logs
                (batch_id, user_id, action, previous_status, new_status, reason)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_rows[code],
                    user_id,
                    action,
                    old_status,
                    new_status,
                    reason,
                ),
            )

        # Packages + public trace for audited batches
        package_data = [
            (
                "PKG-HN-2026-004-001",
                batch_rows["BATCH-HN-2026-004"],
                100,
                "kg",
                "QR-BATCH-HN-2026-004",
                "TRACE-HN-2026-004",
                "ACTIVE",
            ),
            (
                "PKG-HN-2026-006-001",
                batch_rows["BATCH-HN-2026-006"],
                200,
                "kg",
                "QR-BATCH-HN-2026-006",
                "TRACE-HN-2026-006",
                "ACTIVE",
            ),
            (
                "PKG-HN-2026-010-001",
                batch_rows["BATCH-HN-2026-010"],
                150,
                "kg",
                "QR-BATCH-HN-2026-010",
                "TRACE-HN-2026-010",
                "ACTIVE",
            ),
        ]

        conn.executemany(
            """
            INSERT INTO packages
            (package_code, batch_id, quantity, unit, qr_code, trace_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            package_data,
        )

        package_rows = {
            row[1]: row[0]
            for row in conn.execute(
                "SELECT id, package_code FROM packages WHERE package_code LIKE 'PKG-HN-2026-%'"
            ).fetchall()
        }

        trace_data = [
            (
                batch_rows["BATCH-HN-2026-004"],
                package_rows["PKG-HN-2026-004-001"],
                "TRACE-HN-2026-004",
                "https://agrirace.example/trace/TRACE-HN-2026-004",
            ),
            (
                batch_rows["BATCH-HN-2026-006"],
                package_rows["PKG-HN-2026-006-001"],
                "TRACE-HN-2026-006",
                "https://agrirace.example/trace/TRACE-HN-2026-006",
            ),
            (
                batch_rows["BATCH-HN-2026-010"],
                package_rows["PKG-HN-2026-010-001"],
                "TRACE-HN-2026-010",
                "https://agrirace.example/trace/TRACE-HN-2026-010",
            ),
        ]

        conn.executemany(
            """
            INSERT INTO trace_records
            (batch_id, package_id, trace_id, public_url)
            VALUES (?, ?, ?, ?)
            """,
            trace_data,
        )

        conn.commit()

        print("=" * 60)
        print("ĐÃ SEED TEST DATA THÀNH CÔNG")
        print("=" * 60)

        rows = conn.execute(
            """
            SELECT batch_code, product_name, status, quantity, unit
            FROM batches
            WHERE batch_code LIKE 'BATCH-HN-2026-%'
            ORDER BY batch_code
            """
        ).fetchall()

        for row in rows:
            print(f"{row[0]:<22} | {row[1]:<20} | {row[2]:<10} | {row[3]} {row[4]}")

        print()
        print("AUDITED batches có Public Trace:")
        for row in conn.execute(
            """
            SELECT b.batch_code, t.trace_id, p.package_code
            FROM batches b
            JOIN trace_records t ON t.batch_id = b.id
            LEFT JOIN packages p ON p.id = t.package_id
            WHERE b.status = 'AUDITED'
            ORDER BY b.batch_code
            """
        ):
            print(f"{row[0]} | {row[1]} | {row[2]}")

    finally:
        conn.close()


if __name__ == "__main__":
    seed_test_data()
