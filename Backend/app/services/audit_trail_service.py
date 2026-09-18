import json
import sqlite3
from typing import Any

from fastapi import HTTPException


def record_audit_trail(db: sqlite3.Connection, user_id: int | None, action: str, entity_type: str, entity_id: int, old_value: Any = None, new_value: Any = None):
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_trails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            old_value TEXT,
            new_value TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    def normalize(value: Any):
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        return json.dumps(value, ensure_ascii=False)

    db.execute(
        """
        INSERT INTO audit_trails (user_id, action, entity_type, entity_id, old_value, new_value)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            action,
            entity_type,
            entity_id,
            normalize(old_value),
            normalize(new_value),
        ),
    )
    db.commit()
    return {"success": True}


def list_audit_trails(db: sqlite3.Connection, entity_id: int, user: dict[str, Any]):
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_trails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id INTEGER NOT NULL,
            old_value TEXT,
            new_value TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    role = (user or {}).get("role", "").upper()
    if role not in {"ADMIN", "AUDITOR"}:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem lịch sử audit")

    rows = db.execute(
        "SELECT id, user_id, action, entity_type, entity_id, old_value, new_value, created_at FROM audit_trails WHERE entity_id = ? ORDER BY id DESC",
        (entity_id,),
    ).fetchall()
    return [
        {
            "id": row[0],
            "user_id": row[1],
            "action": row[2],
            "entity_type": row[3],
            "entity_id": row[4],
            "old_value": row[5],
            "new_value": row[6],
            "created_at": row[7],
        }
        for row in rows
    ]
