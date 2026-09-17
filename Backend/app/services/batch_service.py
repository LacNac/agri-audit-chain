import sqlite3
from datetime import datetime
from typing import Any
from fastapi import HTTPException


def generate_batch_code() -> str:
    return f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def create_batch(db: sqlite3.Connection, payload: dict[str, Any], farmer_id: int | None = None):
    cursor = db.cursor()
    batch_code = generate_batch_code()

    cursor.execute(
        """
        INSERT INTO batches (
            batch_code, product_name, producer_name, origin, quantity, unit,
            production_date, expiry_date, status, farmer_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'UNVERIFIED', ?)
        """,
        (
            batch_code,
            payload["product_name"],
            payload["producer_name"],
            payload["origin"],
            payload["quantity"],
            payload["unit"],
            payload.get("production_date"),
            payload.get("expiry_date"),
            farmer_id,
        ),
    )
    batch_id = cursor.lastrowid
    db.commit()
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
