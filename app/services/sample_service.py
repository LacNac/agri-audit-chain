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

    existing_batch_sample = db.execute(
        "SELECT id FROM samples WHERE batch_id = ?", (batch_id,)
    ).fetchone()
    if existing_batch_sample:
        raise HTTPException(status_code=409, detail="Batch đã có sample; chỉ được chỉnh sửa sample hiện tại")

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


def update_sample(db: sqlite3.Connection, sample_id: int, payload: dict[str, Any], user_id: int | None = None):
    row = db.execute(
        "SELECT * FROM samples WHERE id = ?", (sample_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sample không tồn tại")

    columns = [col[1] for col in db.execute("PRAGMA table_info(samples)").fetchall()]
    current = dict(zip(columns, row))
    if payload.get("batch_id") != current["batch_id"]:
        raise HTTPException(status_code=400, detail="Không được chuyển sample sang batch khác")

    allowed_fields = {
        "sample_code": "sample_id",
        "sampling_date": "sampling_date",
        "sample_quantity": "sample_quantity",
        "sample_unit": "sample_unit",
        "sampling_location": "sampling_location",
        "sampling_method": "sampling_method",
        "status": "status",
    }
    updates = {}
    for field, payload_key in allowed_fields.items():
        if payload_key in payload and payload[payload_key] is not None:
            updates[field] = payload[payload_key]
    if not updates:
        return _serialize_sample(row, columns)

    if "sample_code" in updates:
        duplicate = db.execute(
            "SELECT id FROM samples WHERE sample_code = ? AND id != ?",
            (updates["sample_code"], sample_id),
        ).fetchone()
        if duplicate:
            raise HTTPException(status_code=400, detail="Sample ID đã tồn tại")

    assignments = ", ".join(f"{field} = ?" for field in updates)
    db.execute(
        f"UPDATE samples SET {assignments} WHERE id = ?",
        [*updates.values(), sample_id],
    )
    db.commit()
    record_audit_trail(
        db,
        user_id=user_id,
        action="UPDATE_SAMPLE",
        entity_type="sample",
        entity_id=sample_id,
        old_value={field: current.get(field) for field in updates},
        new_value=updates,
    )
    updated = db.execute("SELECT * FROM samples WHERE id = ?", (sample_id,)).fetchone()
    return _serialize_sample(updated, columns)


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


def delete_sample(db: sqlite3.Connection, sample_id: int, user_id: int | None = None):
    row = db.execute(
        "SELECT id, batch_id, sample_code FROM samples WHERE id = ?", (sample_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sample không tồn tại")

    db.execute("DELETE FROM samples WHERE id = ?", (sample_id,))
    db.commit()
    record_audit_trail(
        db,
        user_id=user_id,
        action="DELETE_SAMPLE",
        entity_type="sample",
        entity_id=sample_id,
        old_value={"batch_id": row[1], "sample_code": row[2]},
    )
    return {"sample_id": sample_id, "deleted": True}


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
