from fastapi import APIRouter, Depends, HTTPException

from ..dependencies.auth import get_current_user, get_db
from ..dependencies.rbac import require_roles
from ..schema.sample import SampleCreate, SampleOut
from ..services.sample_service import create_sample, get_sample_by_id, list_samples, list_samples_by_batch

router = APIRouter()


@router.post("/samples", response_model=SampleOut)
def create_new_sample(
    payload: SampleCreate,
    db=Depends(get_db),
    user=Depends(require_roles("FARMER", "AUDITOR")),
):
    sample = create_sample(db, payload.batch_id, payload.model_dump(exclude_none=True), user_id=user["id"])
    return SampleOut(**sample)


@router.get("/samples", response_model=list[SampleOut])
def get_all_samples(db=Depends(get_db), user=Depends(get_current_user)):
    rows = list_samples(db, user)
    return [SampleOut(**item) for item in rows]


@router.get("/samples/{sample_id}", response_model=SampleOut)
def get_sample(sample_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    sample = get_sample_by_id(db, sample_id)
    if user["role"] == "FARMER":
        from ..services.batch_service import get_batch_by_id

        batch = get_batch_by_id(db, sample["batch_id"])
        if batch["farmer_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Bạn không có quyền xem sample này")
    return SampleOut(**sample)


@router.get("/batches/{batch_id}/samples", response_model=list[SampleOut])
def get_batch_samples(batch_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    if user["role"] == "FARMER":
        from ..services.batch_service import get_batch_by_id

        batch = get_batch_by_id(db, batch_id)
        if batch["farmer_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Bạn không có quyền xem sample của batch này")
    rows = list_samples_by_batch(db, batch_id)
    return [SampleOut(**item) for item in rows]
