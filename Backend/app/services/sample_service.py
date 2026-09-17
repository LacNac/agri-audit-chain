import sqlite3
from datetime import datetime
from fastapi import HTTPException


def generate_sample_code() -> str:
    return f"SAMPLE-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def create_sample(db: sqlite3.Connection, batch_id: int, payload: dict):
    cursor = db.cursor()
    batch_exists = cursor.execute("SELECT id FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not batch_exists:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    sample_code = payload.get("sample_code") or generate_sample_code()
    cursor.execute(
        """
        INSERT INTO samples (sample_code, batch_id, sample_type, collected_date, source_location, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            sample_code,
            batch_id,
            payload["sample_type"],
            payload.get("collected_date"),
            payload.get("source_location"),
            payload.get("status", "PENDING"),
        ),
    )
    sample_id = cursor.lastrowid
    db.commit()
    return {"id": sample_id, "sample_code": sample_code, "batch_id": batch_id}


def list_samples_by_batch(db: sqlite3.Connection, batch_id: int):
    rows = db.execute("SELECT * FROM samples WHERE batch_id = ? ORDER BY id DESC", (batch_id,)).fetchall()
    columns = [col[1] for col in db.execute("PRAGMA table_info(samples)").fetchall()]
    return [dict(zip(columns, row)) for row in rows]
