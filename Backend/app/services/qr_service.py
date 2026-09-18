import sqlite3
from datetime import datetime

from fastapi import HTTPException

from .audit_trail_service import record_audit_trail


def generate_qr_code(batch_id: int, batch_code: str | None = None) -> str:
    suffix = batch_code or f"BATCH-{batch_id}"
    return f"QR-{suffix}-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def create_qr_record(db: sqlite3.Connection, batch_id: int, user_id: int | None = None, trace_id: str | None = None):
    batch = db.execute("SELECT id, batch_code, status FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    batch_id_db, batch_code, status = batch
    if status != "AUDITED":
        raise HTTPException(status_code=400, detail="Chỉ Batch đã AUDITED mới được tạo QR")

    existing = db.execute(
        "SELECT trace_id, public_url FROM trace_records WHERE batch_id = ? ORDER BY id DESC LIMIT 1",
        (batch_id,),
    ).fetchone()
    if existing:
        trace_id, public_url = existing
        return {"batch_id": batch_id, "trace_id": trace_id, "public_url": public_url, "created": False}

    if trace_id is None:
        trace_id = generate_qr_code(batch_id, batch_code)
    public_url = f"/public/trace/{batch_code}"

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO trace_records (batch_id, trace_id, public_url, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
        (batch_id, trace_id, public_url),
    )
    db.commit()
    record_audit_trail(db, user_id=user_id, action="CREATE_QR", entity_type="qr", entity_id=batch_id, old_value=None, new_value={"trace_id": trace_id, "public_url": public_url})
    return {"batch_id": batch_id, "trace_id": trace_id, "public_url": public_url, "created": True}
