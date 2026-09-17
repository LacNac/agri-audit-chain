import sqlite3
import hashlib
from datetime import datetime
from fastapi import HTTPException


def generate_report_code() -> str:
    return f"REPORT-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def calculate_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def create_report(db: sqlite3.Connection, payload: dict):
    cursor = db.cursor()
    batch_exists = cursor.execute("SELECT id FROM batches WHERE id = ?", (payload["batch_id"],)).fetchone()
    sample_exists = cursor.execute("SELECT id FROM samples WHERE id = ? AND batch_id = ?", (payload["sample_id"], payload["batch_id"])).fetchone()

    if not batch_exists:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")
    if not sample_exists:
        raise HTTPException(status_code=400, detail="Sample không thuộc batch này")

    report_code = generate_report_code()
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
            payload.get("file_name"),
            payload.get("file_hash"),
            payload.get("file_path"),
        ),
    )
    db.commit()
    return {"id": cursor.lastrowid, "report_code": report_code, "status": "PENDING"}


def approve_batch(db: sqlite3.Connection, batch_id: int, user_id: int, reason: str | None = None):
    row = db.execute("SELECT id, status FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    batch_id_db, current_status = row
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
    return {"batch_id": batch_id_db, "status": "AUDITED"}


def reject_batch(db: sqlite3.Connection, batch_id: int, user_id: int, reason: str):
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
        (batch_id_db, user_id, current_status, reason),
    )
    db.commit()
    return {"batch_id": batch_id_db, "status": "REJECTED"}
