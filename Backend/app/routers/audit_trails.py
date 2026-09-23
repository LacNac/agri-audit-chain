from fastapi import APIRouter, Depends, HTTPException

from ..dependencies.auth import get_current_user, get_db
from ..dependencies.rbac import require_roles
from ..services.audit_trail_service import list_audit_trails

router = APIRouter(prefix="/audit-trails", tags=["audit-trails"])


@router.get("")
def search_audit_trails(
    entity_type: str | None = None,
    entity_id: int | None = None,
    action: str | None = None,
    user_id: int | None = None,
    db=Depends(get_db),
    user=Depends(require_roles("ADMIN", "AUDITOR")),
):
    clauses = []
    params = []
    for field, value in (("entity_type", entity_type), ("entity_id", entity_id), ("action", action), ("user_id", user_id)):
        if value is not None:
            clauses.append(f"{field} = ?")
            params.append(value)
    sql = "SELECT id, user_id, action, entity_type, entity_id, old_value, new_value, created_at FROM audit_trails"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY id DESC LIMIT 200"
    rows = db.execute(sql, params).fetchall()
    return [dict(zip(("id", "user_id", "action", "entity_type", "entity_id", "old_value", "new_value", "created_at"), row)) for row in rows]


@router.get("/{entity_id}")
def get_audit_trail(entity_id: int, db=Depends(get_db), user=Depends(require_roles("ADMIN", "AUDITOR"))):
    return list_audit_trails(db, entity_id, user)
