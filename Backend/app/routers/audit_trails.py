from fastapi import APIRouter, Depends, HTTPException

from ..dependencies.auth import get_current_user, get_db
from ..dependencies.rbac import require_roles
from ..services.audit_trail_service import list_audit_trails

router = APIRouter(prefix="/audit-trails", tags=["audit-trails"])


@router.get("/{entity_id}")
def get_audit_trail(entity_id: int, db=Depends(get_db), user=Depends(require_roles("ADMIN", "AUDITOR"))):
    return list_audit_trails(db, entity_id, user)
