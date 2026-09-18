from fastapi import APIRouter, Depends, HTTPException
from ..dependencies.auth import get_current_user, get_db
from ..dependencies.rbac import require_roles
from ..schema.batch import BatchCreate, BatchOut, BatchStatusUpdate, BatchUpdate
from ..services.batch_service import create_batch, delete_batch, get_batch_by_id, list_batches, update_batch
from ..services.qr_service import create_qr_record

router = APIRouter(prefix="/batches", tags=["batches"])


@router.post("", response_model=BatchOut)
def create_new_batch(payload: BatchCreate, db=Depends(get_db), user=Depends(require_roles("FARMER"))):
    result = create_batch(db, payload.model_dump(exclude_none=True), farmer_id=user["id"])
    batch = get_batch_by_id(db, result["id"])
    return BatchOut(**batch)


@router.get("", response_model=list[BatchOut])
def get_all_batches(db=Depends(get_db), user=Depends(get_current_user)):
    if user["role"] == "FARMER":
        farmer_id = user["id"]
    else:
        farmer_id = None
    return [BatchOut(**item) for item in list_batches(db, farmer_id=farmer_id)]


@router.get("/{batch_id}", response_model=BatchOut)
def get_batch(batch_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    batch = get_batch_by_id(db, batch_id)
    if user["role"] == "FARMER" and batch["farmer_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem batch này")
    return BatchOut(**batch)


@router.patch("/{batch_id}", response_model=BatchOut)
def update_batch_details(batch_id: int, payload: BatchUpdate, db=Depends(get_db), user=Depends(require_roles("FARMER"))):
    result = update_batch(db, batch_id, payload.model_dump(exclude_none=True), farmer_id=user["id"])
    return BatchOut(**result)


@router.delete("/{batch_id}")
def delete_batch_details(batch_id: int, db=Depends(get_db), user=Depends(require_roles("FARMER"))):
    return delete_batch(db, batch_id, farmer_id=user["id"])


@router.post("/{batch_id}/qr")
def create_batch_qr(batch_id: int, db=Depends(get_db), user=Depends(require_roles("ADMIN", "AUDITOR", "FARMER"))):
    return create_qr_record(db, batch_id=batch_id, user_id=user["id"])


@router.patch("/{batch_id}/status")
def update_batch_status(batch_id: int, payload: BatchStatusUpdate, db=Depends(get_db), user=Depends(get_current_user)):
    raise HTTPException(status_code=400, detail="Status batch chỉ được thay đổi bởi Auditor approve/reject")
