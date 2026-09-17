from fastapi import APIRouter, Depends, HTTPException
from ..dependencies.auth import get_current_user, get_db
from ..dependencies.rbac import require_permission
from ..schema.batch import BatchCreate, BatchOut, BatchStatusUpdate
from ..services.batch_service import create_batch, list_batches, get_batch_by_id

router = APIRouter(prefix="/batches", tags=["batches"])


@router.post("", response_model=BatchOut)
def create_new_batch(payload: BatchCreate, db=Depends(get_db), user=Depends(require_permission("BATCH_CREATE"))):
    result = create_batch(db, payload.model_dump(), farmer_id=user["id"])
    batch = get_batch_by_id(db, result["id"])
    return BatchOut(**batch)


@router.get("", response_model=list[BatchOut])
def get_all_batches(db=Depends(get_db), user=Depends(get_current_user)):
    farmer_id = user["id"] if user["role"] == "farmer" else None
    return [BatchOut(**item) for item in list_batches(db, farmer_id=farmer_id)]


@router.get("/{batch_id}", response_model=BatchOut)
def get_batch(batch_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    batch = get_batch_by_id(db, batch_id)
    if user["role"] == "farmer" and batch["farmer_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem batch này")
    return BatchOut(**batch)


@router.patch("/{batch_id}/status")
def update_batch_status(batch_id: int, payload: BatchStatusUpdate, db=Depends(get_db), user=Depends(require_permission("AUDIT_VIEW"))):
    batch = get_batch_by_id(db, batch_id)
    db.execute("UPDATE batches SET status = ? WHERE id = ?", (payload.status, batch_id))
    db.commit()
    return {"batch_id": batch_id, "status": payload.status, "reason": payload.reason}
