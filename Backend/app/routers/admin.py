import sqlite3

from fastapi import APIRouter, Depends

from ..dependencies.auth import get_db
from ..dependencies.rbac import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])


def _table_exists(db: sqlite3.Connection, table_name: str) -> bool:
    row = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _safe_count(db: sqlite3.Connection, table_name: str, where_clause: str | None = None, params: tuple = ()) -> int:
    if not _table_exists(db, table_name):
        return 0
    sql = f"SELECT COUNT(*) FROM {table_name}"
    if where_clause:
        sql += f" WHERE {where_clause}"
    return db.execute(sql, params).fetchone()[0]


def _list_batches_by_status(db: sqlite3.Connection, status: str):
    if not _table_exists(db, "batches"):
        return []

    columns = [row[1] for row in db.execute("PRAGMA table_info(batches)").fetchall()]
    selected_columns = ["id", "batch_code", "product_name", "status", "created_at"]
    if "farmer_id" in columns:
        selected_columns.insert(4, "farmer_id")

    select_sql = ", ".join(selected_columns)
    rows = db.execute(
        f"SELECT {select_sql} FROM batches WHERE status = ? ORDER BY created_at DESC, id DESC",
        (status,),
    ).fetchall()

    keys = ["id", "batch_code", "product_name", "status", "created_at"]
    if "farmer_id" in columns:
        keys.insert(4, "farmer_id")

    return [dict(zip(keys, row)) for row in rows]


def _recent_activity(db: sqlite3.Connection):
    if not _table_exists(db, "audit_trails"):
        return []

    rows = db.execute(
        """
        SELECT at.action, at.created_at, u.full_name
        FROM audit_trails at
        LEFT JOIN users u ON u.id = at.user_id
        ORDER BY at.created_at DESC, at.id DESC
        LIMIT 5
        """
    ).fetchall()
    return [
        {"action": row[0], "created_at": row[1], "user_name": row[2] or "Hệ thống"}
        for row in rows
    ]


def _all_batches(db: sqlite3.Connection):
    if not _table_exists(db, "batches"):
        return []

    rows = db.execute(
        """
        SELECT b.id, b.batch_code, b.product_name, b.producer_name,
               b.created_at, b.status, b.farmer_id, u.full_name
        FROM batches b
        LEFT JOIN users u ON u.id = b.farmer_id
        ORDER BY b.created_at DESC, b.id DESC
        """
    ).fetchall()
    return [
        {
            "id": row[0],
            "batch_code": row[1],
            "product_name": row[2],
            "producer_name": row[3] or row[7] or "-",
            "created_at": row[4],
            "status": row[5],
            "farmer_id": row[6],
        }
        for row in rows
    ]


def _all_audit_trails(db: sqlite3.Connection):
    if not _table_exists(db, "audit_trails"):
        return []

    rows = db.execute(
        """
        SELECT at.id, at.created_at, at.user_id, u.full_name, u.role,
               at.action, at.entity_type, at.entity_id
        FROM audit_trails at
        LEFT JOIN users u ON u.id = at.user_id
        ORDER BY at.created_at DESC, at.id DESC
        LIMIT 200
        """
    ).fetchall()
    return [
        {
            "id": row[0],
            "created_at": row[1],
            "user_id": row[2],
            "user_name": row[3] or "Hệ thống",
            "role": row[4] or "SYSTEM",
            "action": row[5],
            "entity_type": row[6],
            "entity_id": row[7],
        }
        for row in rows
    ]


@router.get("/dashboard")
def dashboard(db=Depends(get_db), user=Depends(require_roles("ADMIN"))):
    total_users = _safe_count(db, "users")
    total_farmers = _safe_count(db, "users", "role = 'FARMER' OR role = 'farmer'")
    total_auditors = _safe_count(db, "users", "role = 'AUDITOR' OR role = 'auditor'")
    total_admins = _safe_count(db, "users", "role = 'ADMIN' OR role = 'admin'")
    total_batches = _safe_count(db, "batches")
    audited_batches = _safe_count(db, "batches", "status = 'AUDITED'")
    rejected_batches = _safe_count(db, "batches", "status = 'REJECTED'")
    pending_batches = _safe_count(db, "batches", "status = 'UNVERIFIED'")

    return {
        "summary": {
            "users": total_users,
            "farmers": total_farmers,
            "auditors": total_auditors,
            "admins": total_admins,
            "batches": total_batches,
            "audited_batches": audited_batches,
            "rejected_batches": rejected_batches,
            "pending_batches": pending_batches,
        },
        "lists": {
            "new_batches": _list_batches_by_status(db, "UNVERIFIED"),
            "pending_batches": _list_batches_by_status(db, "UNVERIFIED"),
            "rejected_batches": _list_batches_by_status(db, "REJECTED"),
        },
        "recent_activity": _recent_activity(db),
    }


@router.get("/batches")
def list_admin_batches(db=Depends(get_db), user=Depends(require_roles("ADMIN"))):
    return _all_batches(db)


@router.get("/audit-trails")
def list_admin_audit_trails(db=Depends(get_db), user=Depends(require_roles("ADMIN"))):
    return _all_audit_trails(db)
