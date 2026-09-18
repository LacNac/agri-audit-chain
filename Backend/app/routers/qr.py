from fastapi import APIRouter, Depends

from ..dependencies.auth import get_db
from ..dependencies.rbac import require_roles
from ..services.qr_service import create_qr_record

router = APIRouter(prefix="/qr", tags=["qr"])


@router.post("")
def create_qr(batch_id: int, db=Depends(get_db), user=Depends(require_roles("ADMIN", "AUDITOR", "FARMER"))):
    return create_qr_record(db, batch_id=batch_id, user_id=user["id"])
