import sqlite3
from datetime import datetime
from typing import Any

from fastapi import HTTPException

from .audit_trail_service import record_audit_trail


def generate_sample_code() -> str:
    return f"SAMPLE-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def _serialize_sample(row: tuple[Any, ...], columns: list[str]) -> dict[str, Any]:
    data = dict(zip(columns, row))
    data["sample_id"] = data.get("sample_code") or data.get("id")
    return data


def create_sample(db: sqlite3.Connection, batch_id: int, payload: dict[str, Any], user_id: int | None = None):
    batch_exists = db.execute("SELECT id FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not batch_exists:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    sample_code = payload.get("sample_id") or payload.get("sample_code") or generate_sample_code()
    sample_code = str(sample_code)

    existing = db.execute("SELECT id FROM samples WHERE sample_code = ?", (sample_code,)).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Sample ID đã tồn tại")

    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO samples (
            sample_code, batch_id, sampling_date, sample_quantity, sample_unit,
            sampling_location, sampling_method, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sample_code,
            batch_id,
            payload.get("sampling_date"),
            payload.get("sample_quantity"),
            payload.get("sample_unit"),
            payload.get("sampling_location"),
            payload.get("sampling_method"),
            payload.get("status", "PENDING"),
        ),
    )
    sample_id = cursor.lastrowid
    db.commit()
    record_audit_trail(
        db,
        user_id=user_id,
        action="CREATE_SAMPLE",
        entity_type="sample",
        entity_id=sample_id,
        new_value={"batch_id": batch_id, "sample_code": sample_code},
    )
    row = db.execute("SELECT * FROM samples WHERE id = ?", (sample_id,)).fetchone()
    columns = [col[1] for col in db.execute("PRAGMA table_info(samples)").fetchall()]
    return _serialize_sample(row, columns)


def list_samples_by_batch(db: sqlite3.Connection, batch_id: int):
    rows = db.execute(
        "SELECT * FROM samples WHERE batch_id = ? ORDER BY id DESC",
        (batch_id,),
    ).fetchall()
    columns = [col[1] for col in db.execute("PRAGMA table_info(samples)").fetchall()]
    return [_serialize_sample(row, columns) for row in rows]


def list_samples(db: sqlite3.Connection, user: dict[str, Any]):
    if user["role"] == "FARMER":
        rows = db.execute(
            "SELECT s.* FROM samples s JOIN batches b ON b.id = s.batch_id WHERE b.farmer_id = ? ORDER BY s.id DESC",
            (user["id"],),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM samples ORDER BY id DESC").fetchall()

    columns = [col[1] for col in db.execute("PRAGMA table_info(samples)").fetchall()]
    return [_serialize_sample(row, columns) for row in rows]


def get_sample_by_id(db: sqlite3.Connection, sample_id: str | int):
    try:
        numeric_id = int(sample_id)
    except (TypeError, ValueError):
        numeric_id = None

    if numeric_id is not None:
        row = db.execute(
            "SELECT * FROM samples WHERE id = ? OR sample_code = ? ORDER BY id DESC LIMIT 1",
            (numeric_id, str(sample_id)),
        ).fetchone()
    else:
        row = db.execute("SELECT * FROM samples WHERE sample_code = ? ORDER BY id DESC LIMIT 1", (str(sample_id),)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Sample không tồn tại")

    columns = [col[1] for col in db.execute("PRAGMA table_info(samples)").fetchall()]
    return _serialize_sample(row, columns)
