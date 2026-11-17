from io import BytesIO

import qrcode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from ..dependencies.auth import get_current_user, get_db
from ..dependencies.rbac import require_roles
from ..services.batch_service import get_batch_by_id
from ..services.qr_service import create_qr_record

router = APIRouter(prefix="/qr", tags=["qr"])


def _require_farmer_batch_access(batch_id: int, db, user):
    batch = get_batch_by_id(db, batch_id)
    if batch["farmer_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Bạn không có quyền tạo QR cho batch này")
    return batch


@router.get("/{batch_id}/image")
def get_qr_image(batch_id: int, db=Depends(get_db), user=Depends(require_roles("FARMER"))):
    _require_farmer_batch_access(batch_id, db, user)
    result = create_qr_record(db, batch_id=batch_id, user_id=user["id"])
    target_url = f"http://127.0.0.1:5500{result['public_url']}"
    image = qrcode.make(target_url)
    output = BytesIO()
    image.save(output, "PNG")
    output.seek(0)
    return StreamingResponse(output, media_type="image/png", headers={"Content-Disposition": f"inline; filename=qr-{batch_id}.png"})
