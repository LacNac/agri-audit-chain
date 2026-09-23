import sqlite3
from datetime import datetime
from typing import Any
from fastapi import HTTPException

from .audit_trail_service import record_audit_trail


def generate_batch_code() -> str:
    return f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def create_batch(db: sqlite3.Connection, payload: dict[str, Any], farmer_id: int | None = None):
    if farmer_id is None:
        raise HTTPException(status_code=401, detail="Không xác định farmer hiện tại")

    clean_payload = dict(payload)
    clean_payload.pop("farmer_id", None)

    product_name = clean_payload.get("product_name")
    product_type = clean_payload.get("product_type")
    origin = clean_payload.get("origin")
    quantity = clean_payload.get("quantity")
    unit = clean_payload.get("unit")
    production_date = clean_payload.get("production_date")
    note = clean_payload.get("note")

    if not product_name or not product_type or not origin or quantity is None or not unit:
        raise HTTPException(status_code=400, detail="Thiếu thông tin bắt buộc của Batch")

    producer_name = clean_payload.get("producer_name")
    try:
        farmer_row = db.execute("SELECT full_name FROM users WHERE id = ?", (farmer_id,)).fetchone()
        if not producer_name and farmer_row:
            producer_name = farmer_row[0]
    except sqlite3.DatabaseError:
        farmer_row = None

    cursor = db.cursor()
    batch_code = generate_batch_code()

    cursor.execute(
        """
        INSERT INTO batches (
            batch_code, product_name, product_type, producer_name, origin, quantity, unit,
            production_date, expiry_date, status, farmer_id, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'UNVERIFIED', ?, ?)
        """,
        (
            batch_code,
            product_name,
            product_type,
            producer_name,
            origin,
            quantity,
            unit,
            production_date,
            clean_payload.get("expiry_date"),
            farmer_id,
            note,
        ),
    )
    batch_id = cursor.lastrowid
    db.commit()
    record_audit_trail(db, user_id=farmer_id, action="CREATE_BATCH", entity_type="batch", entity_id=batch_id, old_value=None, new_value={"batch_code": batch_code, "product_name": product_name, "status": "UNVERIFIED"})
    return {"id": batch_id, "batch_code": batch_code, "status": "UNVERIFIED"}


def list_batches(db: sqlite3.Connection, farmer_id: int | None = None):
    if farmer_id is not None:
        rows = db.execute(
            "SELECT * FROM batches WHERE farmer_id = ? ORDER BY id DESC",
            (farmer_id,),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM batches ORDER BY id DESC").fetchall()

    columns = [col[1] for col in db.execute("PRAGMA table_info(batches)").fetchall()]
    return [dict(zip(columns, row)) for row in rows]


def get_batch_by_id(db: sqlite3.Connection, batch_id: int):
    row = db.execute("SELECT * FROM batches WHERE id = ?", (batch_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")
    columns = [col[1] for col in db.execute("PRAGMA table_info(batches)").fetchall()]
    return dict(zip(columns, row))


def update_batch(db: sqlite3.Connection, batch_id: int, payload: dict[str, Any], farmer_id: int):
    batch = get_batch_by_id(db, batch_id)

    if batch["farmer_id"] != farmer_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền sửa batch này")

    if batch["status"] not in {"UNVERIFIED", "REJECTED"}:
        raise HTTPException(status_code=403, detail="Batch ở trạng thái AUDITED, không được sửa hoặc xóa")

    if "status" in payload:
        raise HTTPException(status_code=400, detail="Status batch chỉ được thay đổi bởi Auditor approve/reject")

    allowed_fields = {
        "product_name",
        "product_type",
        "origin",
        "quantity",
        "unit",
        "production_date",
        "expiry_date",
        "note",
    }
    updates = {key: value for key, value in payload.items() if key in allowed_fields and value is not None}
    if not updates:
        return batch

    previous = get_batch_by_id(db, batch_id)
    assignments = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [batch_id]
    db.execute(f"UPDATE batches SET {assignments} WHERE id = ?", values)
    if batch["status"] == "REJECTED":
        db.execute("UPDATE batches SET status = 'UNVERIFIED' WHERE id = ?", (batch_id,))
    db.commit()
    record_audit_trail(db, user_id=farmer_id, action="UPDATE_BATCH", entity_type="batch", entity_id=batch_id, old_value={k: previous.get(k) for k in updates}, new_value={k: updates[k] for k in updates})
    return get_batch_by_id(db, batch_id)


def delete_batch(db: sqlite3.Connection, batch_id: int, farmer_id: int):
    batch = get_batch_by_id(db, batch_id)

    if batch["farmer_id"] != farmer_id:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa batch này")

    if batch["status"] == "UNVERIFIED":
        db.execute("DELETE FROM batches WHERE id = ?", (batch_id,))
        db.commit()
        return {"batch_id": batch_id, "deleted": True}

    if batch["status"] == "REJECTED":
        raise HTTPException(status_code=403, detail="Batch REJECTED không được phép xóa")

    raise HTTPException(status_code=403, detail="Batch ở trạng thái AUDITED, không được sửa hoặc xóa")
