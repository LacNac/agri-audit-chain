from io import BytesIO

import qrcode
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..dependencies.auth import get_db
from ..dependencies.rbac import require_roles
from ..services.qr_service import create_qr_record

router = APIRouter(prefix="/qr", tags=["qr"])


@router.post("")
def create_qr(batch_id: int, db=Depends(get_db), user=Depends(require_roles("AUDITOR"))):
    return create_qr_record(db, batch_id=batch_id, user_id=user["id"])


@router.get("/{batch_id}/image")
def get_qr_image(batch_id: int, db=Depends(get_db), user=Depends(require_roles("AUDITOR"))):
    result = create_qr_record(db, batch_id=batch_id, user_id=user["id"])
    target_url = f"http://127.0.0.1:5500{result['public_url']}"
    image = qrcode.make(target_url)
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return StreamingResponse(output, media_type="image/png", headers={"Content-Disposition": f"inline; filename=qr-{batch_id}.png"})
