import sqlite3
import hashlib
from datetime import datetime
from fastapi import HTTPException

from .audit_trail_service import record_audit_trail


def generate_report_code() -> str:
    return f"REPORT-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def calculate_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def create_report(db: sqlite3.Connection, payload: dict, file_bytes: bytes | None = None):
    if payload.get("file_hash"):
        raise HTTPException(status_code=400, detail="Hash PDF không được nhập thủ công; hệ thống tự tính từ file upload")

    if file_bytes is None:
        raise HTTPException(status_code=400, detail="Thiếu file PDF để tính SHA-256")

    cursor = db.cursor()
    batch_exists = cursor.execute("SELECT id FROM batches WHERE id = ?", (payload["batch_id"],)).fetchone()
    sample_exists = cursor.execute("SELECT id FROM samples WHERE id = ? AND batch_id = ?", (payload["sample_id"], payload["batch_id"])).fetchone()

    if not batch_exists:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")
    if not sample_exists:
        raise HTTPException(status_code=400, detail="Sample không thuộc batch này")

    report_code = generate_report_code()
    file_hash = calculate_sha256(file_bytes)
    file_name = payload.get("file_name") or f"{report_code}.pdf"
    file_path = payload.get("file_path") or f"/uploads/{report_code}.pdf"

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
            payload.get("result"),
            file_name,
            file_hash,
            file_path,
        ),
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
        SELECT lr.id, lr.file_hash, lr.file_path, lr.report_code
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

    report_id, file_hash, file_path, report_code = report_row
    if not file_hash or not file_path or len(file_hash.strip()) != 64:
        raise HTTPException(status_code=400, detail="Batch chưa đủ thông tin để kiểm định")

    return {"report_id": report_id, "report_code": report_code, "file_hash": file_hash, "file_path": file_path}


def approve_batch(db: sqlite3.Connection, batch_id: int, user_id: int, reason: str | None = None):
    row = db.execute("SELECT id, status FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    batch_id_db, current_status = row
    validate_batch_report_integrity(db, batch_id)

    if current_status == "AUDITED":
        raise HTTPException(status_code=400, detail="Batch đã được phê duyệt")

    db.execute(
        "UPDATE batches SET status = 'AUDITED' WHERE id = ?",
        (batch_id,),
    )
    db.execute(
        "INSERT INTO audit_logs (batch_id, user_id, action, previous_status, new_status, reason) VALUES (?, ?, 'APPROVE', ?, 'AUDITED', ?)",
        (batch_id_db, user_id, current_status, reason or "Auditor approved"),
    )
    db.commit()
    record_audit_trail(db, user_id=user_id, action="APPROVE_BATCH", entity_type="batch", entity_id=batch_id_db, old_value={"status": current_status}, new_value={"status": "AUDITED", "reason": reason or "Auditor approved"})
    return {"batch_id": batch_id_db, "status": "AUDITED"}


def reject_batch(db: sqlite3.Connection, batch_id: int, user_id: int, reason: str):
    if not reason or not reason.strip():
        raise HTTPException(status_code=400, detail="Cần nhập lý do từ chối")

    row = db.execute("SELECT id, status FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    batch_id_db, current_status = row
    db.execute(
        "UPDATE batches SET status = 'REJECTED' WHERE id = ?",
        (batch_id,),
    )
    db.execute(
        "INSERT INTO audit_logs (batch_id, user_id, action, previous_status, new_status, reason) VALUES (?, ?, 'REJECT', ?, 'REJECTED', ?)",
        (batch_id_db, user_id, current_status, reason.strip()),
    )
    db.commit()
    record_audit_trail(db, user_id=user_id, action="REJECT_BATCH", entity_type="batch", entity_id=batch_id_db, old_value={"status": current_status}, new_value={"status": "REJECTED", "reason": reason.strip()})
    return {"batch_id": batch_id_db, "status": "REJECTED"}
