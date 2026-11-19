import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException

from .audit_trail_service import record_audit_trail
from .cold_chain_service import (
    enqueue_batch_sync,
    ensure_batch_not_in_transit,
    process_cold_chain_outbox,
)
from .notification_service import create_notification
from .qr_service import create_qr_record

UPLOADS_DIR = Path(__file__).resolve().parents[2] / "uploads"


def _ensure_integrity_table(db: sqlite3.Connection):
    create_sqlite_table = isinstance(db, sqlite3.Connection)
    id_column = "INTEGER PRIMARY KEY AUTOINCREMENT" if create_sqlite_table else "SERIAL PRIMARY KEY"
    db.execute(f"""
        CREATE TABLE IF NOT EXISTS integrity_proofs (
            id {id_column},
            report_id INTEGER NOT NULL UNIQUE,
            batch_id INTEGER NOT NULL,
            file_hash TEXT NOT NULL,
            previous_proof TEXT,
            proof_hash TEXT NOT NULL,
            created_at {"DATETIME" if create_sqlite_table else "TIMESTAMP WITHOUT TIME ZONE"} DEFAULT CURRENT_TIMESTAMP
        )
    """)


def generate_report_code() -> str:
    return f"REPORT-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"


def calculate_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def create_report(db: sqlite3.Connection, payload: dict, file_bytes: bytes | None = None):
    if payload.get("file_hash"):
        raise HTTPException(status_code=400, detail="Hash PDF không được nhập thủ công; hệ thống tự tính từ file upload")

    if file_bytes is None:
        raise HTTPException(status_code=400, detail="Thiếu file PDF để tính SHA-256")

    result = str(payload.get("result") or "").strip().upper()
    if result not in {"PASS", "FAIL"}:
        raise HTTPException(status_code=400, detail="Kết quả report phải là PASS hoặc FAIL")

    cursor = db.cursor()
    batch_exists = cursor.execute("SELECT id FROM batches WHERE id = ?", (payload["batch_id"],)).fetchone()
    sample_exists = cursor.execute("SELECT id FROM samples WHERE id = ? AND batch_id = ?", (payload["sample_id"], payload["batch_id"])).fetchone()

    if not batch_exists:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")
    if not sample_exists:
        raise HTTPException(status_code=400, detail="Sample không thuộc batch này")

    batch_status, batch_code = cursor.execute(
        "SELECT status, batch_code FROM batches WHERE id = ?", (payload["batch_id"],)
    ).fetchone()
    if batch_status == "AUDITED":
        raise HTTPException(status_code=403, detail="Batch đã AUDITED, không được bổ sung hoặc thay thế report")
    ensure_batch_not_in_transit(batch_code)

    report_code = generate_report_code()
    file_hash = calculate_sha256(file_bytes)
    file_name = payload.get("file_name") or f"{report_code}.pdf"
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{report_code}.pdf"
    (UPLOADS_DIR / stored_name).write_bytes(file_bytes)
    file_path = f"/uploads/{stored_name}"

    cursor.execute(
        """
        INSERT INTO lab_reports (report_code, sample_id, batch_id, lab_name, lab_code, report_date, result, file_name, file_hash, file_path, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
        """,
        (
            report_code,
            payload["sample_id"],
            payload["batch_id"],
            payload.get("lab_name"),
            payload.get("lab_code"),
            payload.get("report_date"),
            result,
            file_name,
            file_hash,
            file_path,
        ),
    )
    db.commit()
    _ensure_integrity_table(db)
    previous = db.execute("SELECT proof_hash FROM integrity_proofs ORDER BY id DESC LIMIT 1").fetchone()
    previous_proof = previous[0] if previous else ""
    proof_hash = hashlib.sha256(f"{previous_proof}:{cursor.lastrowid}:{payload['batch_id']}:{file_hash}".encode()).hexdigest()
    db.execute(
        "INSERT INTO integrity_proofs (report_id, batch_id, file_hash, previous_proof, proof_hash) VALUES (?, ?, ?, ?, ?)",
        (cursor.lastrowid, payload["batch_id"], file_hash, previous_proof or None, proof_hash),
    )
    db.commit()
    record_audit_trail(db, user_id=None, action="UPLOAD_LAB_REPORT", entity_type="lab_report", entity_id=cursor.lastrowid, old_value=None, new_value={"report_code": report_code, "sample_id": payload["sample_id"], "batch_id": payload["batch_id"], "file_hash": file_hash})
    return {
        "id": cursor.lastrowid,
        "report_code": report_code,
        "file_name": file_name,
        "file_hash": file_hash,
        "file_path": file_path,
        "status": "PENDING",
        "result": result,
        "proof_hash": proof_hash,
    }

def update_report(db: sqlite3.Connection, report_id: int, payload: dict, file_bytes: bytes | None = None, user_id: int | None = None):
    report = get_report(db, report_id)
    batch_status, batch_code = db.execute(
        "SELECT status, batch_code FROM batches WHERE id = ?", (report["batch_id"],)
    ).fetchone()
    if batch_status == "AUDITED":
        raise HTTPException(status_code=403, detail="Batch đã AUDITED, không được sửa report")
    ensure_batch_not_in_transit(batch_code)

    result = str(payload.get("result") or "").strip().upper()
    lab_name = str(payload.get("lab_name") or "").strip()
    lab_code = str(payload.get("lab_code") or "").strip()
    if result not in {"PASS", "FAIL"}:
        raise HTTPException(status_code=422, detail="Kết quả report phải là PASS hoặc FAIL")
    if len(lab_name) < 2 or len(lab_code) < 2:
        raise HTTPException(status_code=422, detail="Tên và mã phòng lab không được để trống")
    if not db.execute(
        "SELECT id FROM samples WHERE id = ? AND batch_id = ?",
        (payload["sample_id"], report["batch_id"]),
    ).fetchone():
        raise HTTPException(status_code=400, detail="Sample không thuộc batch này")

    file_hash = report["file_hash"]
    file_path = report["file_path"]
    file_name = report["file_name"]
    old_file_path = file_path
    if file_bytes is not None:
        file_hash = calculate_sha256(file_bytes)
        file_name = payload.get("file_name") or file_name
        stored_name = f"{report['report_code']}.pdf"
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        (UPLOADS_DIR / stored_name).write_bytes(file_bytes)
        file_path = f"/uploads/{stored_name}"

    db.execute(
        """
        UPDATE lab_reports
        SET sample_id = ?, lab_name = ?, lab_code = ?, report_date = ?, result = ?,
            file_name = ?, file_hash = ?, file_path = ?
        WHERE id = ?
        """,
        (
            payload["sample_id"], lab_name, lab_code, payload.get("report_date"),
            result, file_name, file_hash, file_path, report_id,
        ),
    )
    _ensure_integrity_table(db)
    proof = db.execute(
        "SELECT previous_proof FROM integrity_proofs WHERE report_id = ?", (report_id,)
    ).fetchone()
    previous_proof = (proof[0] if proof else None) or ""
    proof_hash = hashlib.sha256(
        f"{previous_proof}:{report_id}:{report['batch_id']}:{file_hash}".encode()
    ).hexdigest()
    db.execute(
        """
        INSERT INTO integrity_proofs (report_id, batch_id, file_hash, previous_proof, proof_hash)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(report_id) DO UPDATE SET
            file_hash = excluded.file_hash,
            proof_hash = excluded.proof_hash
        """,
        (report_id, report["batch_id"], file_hash, previous_proof or None, proof_hash),
    )
    record_audit_trail(
        db,
        user_id=user_id,
        action="UPDATE_LAB_REPORT",
        entity_type="lab_report",
        entity_id=report_id,
        old_value={"file_name": report["file_name"], "result": report["result"], "lab_name": report["lab_name"], "lab_code": report["lab_code"], "file_hash": report["file_hash"]},
        new_value={"file_name": file_name, "result": result, "lab_name": lab_name, "lab_code": lab_code, "file_hash": file_hash},
    )
    db.commit()

    if file_bytes is not None and old_file_path and old_file_path != file_path:
        old_file = (UPLOADS_DIR / Path(old_file_path).name).resolve()
        if old_file.parent == UPLOADS_DIR.resolve() and old_file.is_file():
            old_file.unlink()
    updated = get_report(db, report_id)
    updated["proof_hash"] = proof_hash
    return updated


def get_report(db: sqlite3.Connection, report_id: int):
    row = db.execute("SELECT * FROM lab_reports WHERE id = ?", (report_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Report không tồn tại")
    columns = [column[1] for column in db.execute("PRAGMA table_info(lab_reports)").fetchall()]
    report = dict(zip(columns, row))
    _ensure_integrity_table(db)
    proof = db.execute(
        "SELECT previous_proof, proof_hash FROM integrity_proofs WHERE report_id = ?",
        (report_id,),
    ).fetchone()
    report["previous_proof"] = proof[0] if proof else None
    report["proof_hash"] = proof[1] if proof else None
    return report


def list_reports_by_batch(db: sqlite3.Connection, batch_id: int):
    if not db.execute("SELECT id FROM batches WHERE id = ?", (batch_id,)).fetchone():
        raise HTTPException(status_code=404, detail="Batch không tồn tại")
    rows = db.execute("SELECT * FROM lab_reports WHERE batch_id = ? ORDER BY id DESC", (batch_id,)).fetchall()
    columns = [column[1] for column in db.execute("PRAGMA table_info(lab_reports)").fetchall()]
    reports = []
    for row in rows:
        report = dict(zip(columns, row))
        _ensure_integrity_table(db)
        proof = db.execute(
            "SELECT previous_proof, proof_hash FROM integrity_proofs WHERE report_id = ?",
            (report["id"],),
        ).fetchone()
        report["previous_proof"] = proof[0] if proof else None
        report["proof_hash"] = proof[1] if proof else None
        reports.append(report)
    return reports


def verify_report_integrity(db: sqlite3.Connection, report_id: int):
    report = get_report(db, report_id)
    file_name = Path(report.get("file_path") or report.get("file_name") or "").name
    file_path = (UPLOADS_DIR / file_name).resolve()
    if file_path.parent != UPLOADS_DIR.resolve() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File report không tồn tại")
    actual_hash = calculate_sha256(file_path.read_bytes())
    _ensure_integrity_table(db)
    proof = db.execute(
        "SELECT file_hash, previous_proof, proof_hash FROM integrity_proofs WHERE report_id = ?",
        (report_id,),
    ).fetchone()
    hash_valid = actual_hash == report.get("file_hash")
    previous_proof = (proof[1] if proof else None) or ""
    calculated_proof_hash = hashlib.sha256(
        f"{previous_proof}:{report_id}:{report['batch_id']}:{actual_hash}".encode()
    ).hexdigest()
    proof_valid = bool(
        proof
        and proof[0] == report.get("file_hash")
        and calculated_proof_hash == proof[2]
    )
    return {
        "report_id": report_id,
        "stored_hash": report.get("file_hash"),
        "actual_hash": actual_hash,
        "hash_valid": hash_valid,
        "proof_hash": proof[2] if proof else None,
        "calculated_proof_hash": calculated_proof_hash,
        "proof_valid": proof_valid,
        "valid": hash_valid and proof_valid,
    }


def validate_batch_report_integrity(db: sqlite3.Connection, batch_id: int):
    batch_row = db.execute("SELECT id FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not batch_row:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    sample_count = db.execute("SELECT COUNT(*) FROM samples WHERE batch_id = ?", (batch_id,)).fetchone()[0]
    if sample_count == 0:
        raise HTTPException(status_code=400, detail="Batch chưa đủ thông tin để kiểm định")

    report_row = db.execute(
        """
        SELECT lr.id, lr.file_hash, lr.file_path, lr.report_code, lr.result
        FROM lab_reports lr
        JOIN samples s ON s.id = lr.sample_id
        WHERE s.batch_id = ?
        ORDER BY lr.id DESC
        LIMIT 1
        """,
        (batch_id,),
    ).fetchone()

    if not report_row:
        raise HTTPException(status_code=400, detail="Batch chưa đủ thông tin để kiểm định")

    report_id, file_hash, file_path, report_code, result = report_row
    if not file_hash or not file_path or len(file_hash.strip()) != 64:
        raise HTTPException(status_code=400, detail="Batch chưa đủ thông tin để kiểm định")

    if not verify_report_integrity(db, report_id)["valid"]:
        raise HTTPException(status_code=400, detail="Report hoặc Proof of Integrity không hợp lệ")

    return {
        "report_id": report_id,
        "report_code": report_code,
        "file_hash": file_hash,
        "file_path": file_path,
        "result": (result or "").strip().upper(),
    }


def get_latest_batch_report_result(db: sqlite3.Connection, batch_id: int) -> str:
    report = db.execute(
        "SELECT result FROM lab_reports WHERE batch_id = ? ORDER BY id DESC LIMIT 1",
        (batch_id,),
    ).fetchone()
    result = report[0].strip().upper() if report and report[0] else ""
    if result not in {"PASS", "FAIL"}:
        raise HTTPException(status_code=400, detail="Batch bắt buộc phải có Laboratory Test Report với kết quả PASS hoặc FAIL")
    return result


def approve_batch(
    db: sqlite3.Connection,
    batch_id: int,
    user_id: int,
    reason: str | None = None,
    destination: str | None = None,
):
    row = db.execute(
        "SELECT id, status, batch_code, destination FROM batches WHERE id = ?", (batch_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    batch_id_db, current_status, batch_code, current_destination = row
    if current_status not in {"UNVERIFIED", "REJECTED"}:
        raise HTTPException(status_code=400, detail="Batch không ở trạng thái có thể phê duyệt")
    ensure_batch_not_in_transit(batch_code)
    validate_batch_report_integrity(db, batch_id)
    report_result = get_latest_batch_report_result(db, batch_id)
    if report_result != "PASS":
        raise HTTPException(status_code=400, detail="Chỉ được approve batch khi lab report có trạng thái PASS")

    batch_cols = {col[1] for col in db.execute("PRAGMA table_info(batches)").fetchall()}
    assignments = ["status = 'AUDITED'"]
    params = []
    if "reason" in batch_cols:
        assignments.append("reason = ?")
        params.append(reason or "Auditor approved")
    destination = destination.strip() if destination is not None else None
    if destination:
        assignments.append("destination = ?")
        params.append(destination)
    if "return_goods" in batch_cols:
        assignments.append("return_goods = 0")
    if "return_requested" in batch_cols:
        assignments.append("return_requested = 0")
    params.append(batch_id)

    db.execute(
        f"UPDATE batches SET {', '.join(assignments)} WHERE id = ?",
        params,
    )
    db.commit()

    qr_record = create_qr_record(db, batch_id=batch_id, user_id=user_id)
    full_batch = db.execute(
        "SELECT batch_code, farmer_id, product_name, producer_name FROM batches WHERE id = ?",
        (batch_id,),
    ).fetchone()
    batch_code, farmer_id, product_name, producer_name = full_batch

    create_notification(
        db,
        recipient_role="FARMER",
        recipient_user_id=farmer_id,
        title=f"Lô hàng {batch_code} đã được kiểm định (AUDITED)",
        message=f"Lô hàng {product_name or ''} ({batch_code}) đã được Auditor phê duyệt đạt chất lượng. Mã QR truy xuất đã được kích hoạt.",
        batch_id=batch_id_db,
        notification_type="BATCH_AUDITED",
    )
    create_notification(
        db,
        recipient_role="COLD_CHAIN",
        title=f"Lô hàng {batch_code} đã kiểm định đạt (AUDITED)",
        message=f"Lô hàng {product_name or ''} ({batch_code}) của nông dân {producer_name or ''} đã hoàn tất kiểm định AUDITED thành công.",
        batch_id=batch_id_db,
        notification_type="BATCH_AUDITED",
    )

    record_audit_trail(
        db,
        user_id=user_id,
        action="APPROVE_BATCH",
        entity_type="batch",
        entity_id=batch_id_db,
        old_value={"status": current_status, "destination": current_destination},
        new_value={
            "status": "AUDITED",
            "reason": reason or "Auditor approved",
            "destination": destination or current_destination,
        },
    )
    enqueue_batch_sync(db, batch_id_db)
    process_cold_chain_outbox(db)
    return {
        "batch_id": batch_id_db,
        "status": "AUDITED",
        "destination": destination or current_destination,
        "qr": qr_record,
    }


def reject_batch(db: sqlite3.Connection, batch_id: int, user_id: int, reason: str, return_goods: bool = False):
    if not reason or not reason.strip():
        raise HTTPException(status_code=400, detail="Cần nhập lý do từ chối")

    row = db.execute(
        "SELECT id, status, batch_code FROM batches WHERE id = ?", (batch_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    batch_id_db, current_status, batch_code = row
    if current_status not in {"UNVERIFIED", "REJECTED"}:
        raise HTTPException(status_code=400, detail="Batch không ở trạng thái có thể từ chối")
    ensure_batch_not_in_transit(batch_code)
    get_latest_batch_report_result(db, batch_id)
    rejection_reason = reason.strip()

    batch_cols = {col[1] for col in db.execute("PRAGMA table_info(batches)").fetchall()}
    assignments = ["status = 'REJECTED'"]
    params = []
    if "reason" in batch_cols:
        assignments.append("reason = ?")
        params.append(rejection_reason)
    if "return_goods" in batch_cols:
        assignments.append("return_goods = ?")
        params.append(1 if return_goods else 0)
    if "rejected_at" in batch_cols:
        assignments.append("rejected_at = CURRENT_TIMESTAMP")
    if "return_requested" in batch_cols:
        assignments.append("return_requested = ?")
        params.append(1 if return_goods else 0)
    params.append(batch_id)

    db.execute(
        f"UPDATE batches SET {', '.join(assignments)} WHERE id = ?",
        params,
    )
    db.commit()

    full_batch = db.execute(
        "SELECT batch_code, farmer_id, product_name, producer_name FROM batches WHERE id = ?",
        (batch_id,),
    ).fetchone()
    batch_code, farmer_id, product_name, producer_name = full_batch

    if return_goods:
        create_notification(
            db,
            recipient_role="FARMER",
            recipient_user_id=farmer_id,
            title=f"Lô hàng {batch_code} bị từ chối - Yêu cầu trả hàng",
            message=f"Lô hàng {product_name or ''} ({batch_code}) bị từ chối kiểm định. Lý do: {rejection_reason}. Auditor đã chọn ô Trả hàng; hàng sẽ được công ty kho lạnh hoàn trả cho bạn.",
            batch_id=batch_id_db,
            notification_type="RETURN_REQUESTED",
        )
        create_notification(
            db,
            recipient_role="COLD_CHAIN",
            title=f"Yêu cầu trả hàng: Lô hàng {batch_code}",
            message=f"Lô hàng {product_name or ''} ({batch_code}) của nông dân {producer_name or ''} bị từ chối kiểm định (Lý do: {rejection_reason}). Auditor đã tích chọn Trả hàng; yêu cầu công ty kho lạnh tiến hành trả hàng cho nông dân.",
            batch_id=batch_id_db,
            notification_type="RETURN_REQUESTED",
        )
    else:
        create_notification(
            db,
            recipient_role="FARMER",
            recipient_user_id=farmer_id,
            title=f"Lô hàng {batch_code} cần cập nhật thông tin (24h)",
            message=f"Lô hàng {product_name or ''} ({batch_code}) bị từ chối kiểm định vì: {rejection_reason}. Ô Trả hàng KHÔNG được chọn. Bạn có 24 giờ để cập nhật lại thông tin sản phẩm và gửi lại kiểm định. Sau 24h nếu không cập nhật, hệ thống sẽ tự động yêu cầu kho lạnh trả hàng.",
            batch_id=batch_id_db,
            notification_type="BATCH_REJECTED",
        )
        create_notification(
            db,
            recipient_role="COLD_CHAIN",
            title=f"Thông báo lô hàng {batch_code} bị từ chối kiểm định",
            message=f"Lô hàng {product_name or ''} ({batch_code}) của nông dân {producer_name or ''} bị từ chối (Lý do: {rejection_reason}). Ô Trả hàng chưa được chọn; đang chờ nông dân cập nhật thông tin trong vòng 24h.",
            batch_id=batch_id_db,
            notification_type="BATCH_REJECTED",
        )

    record_audit_trail(
        db,
        user_id=user_id,
        action="REJECT_BATCH",
        entity_type="batch",
        entity_id=batch_id_db,
        old_value={"status": current_status},
        new_value={"status": "REJECTED", "reason": rejection_reason, "return_goods": return_goods},
    )
    enqueue_batch_sync(db, batch_id_db)
    process_cold_chain_outbox(db)
    return {"batch_id": batch_id_db, "status": "REJECTED", "return_goods": return_goods}
