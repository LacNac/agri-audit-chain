from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from ..dependencies.auth import get_current_user, get_db
from ..dependencies.rbac import require_roles
from ..schema.batch import BatchCreate, BatchOut, BatchStatusUpdate, BatchUpdate
from ..services.batch_service import create_batch, delete_batch, get_batch_by_id, list_batches, submit_batch, update_batch
from ..services.qr_service import create_qr_record

router = APIRouter(prefix="/batches", tags=["batches"])
UPLOADS_DIR = Path(__file__).resolve().parents[2] / "uploads"


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


@router.get("/{batch_id}/report-file")
def get_batch_report_file(batch_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    batch = get_batch_by_id(db, batch_id)
    if user["role"] == "FARMER" and batch["farmer_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem report này")

    report = db.execute(
        "SELECT file_name, file_path FROM lab_reports WHERE batch_id = ? ORDER BY id DESC LIMIT 1",
        (batch_id,),
    ).fetchone()
    if not report:
        raise HTTPException(status_code=404, detail="Batch chưa có report")

    file_name, file_path = report
    requested_name = Path(file_path or file_name or "").name
    report_path = (UPLOADS_DIR / requested_name).resolve()
    if report_path.parent != UPLOADS_DIR.resolve() or not report_path.is_file():
        raise HTTPException(status_code=404, detail="File report không tồn tại")
    return FileResponse(report_path, media_type="application/pdf", filename=file_name or requested_name)


@router.get("/{batch_id}/rejection")
def get_batch_rejection(batch_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    batch = get_batch_by_id(db, batch_id)
    if user["role"] == "FARMER" and batch["farmer_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem batch này")
    row = db.execute(
        """
        SELECT user_id, new_value, created_at
        FROM audit_trails
        WHERE entity_type = 'batch' AND entity_id = ? AND action = 'REJECT_BATCH'
        ORDER BY id DESC LIMIT 1
        """,
        (batch_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Batch chưa có lý do Reject")
    import json
    details = json.loads(row[1]) if row[1] else {}
    return {"batch_id": batch_id, "reason": details.get("reason"), "rejected_by": row[0], "rejected_at": row[2]}


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


@router.post("/{batch_id}/submit")
def submit_batch_for_audit(batch_id: int, db=Depends(get_db), user=Depends(require_roles("FARMER"))):
    return submit_batch(db, batch_id, farmer_id=user["id"])


@router.post("/{batch_id}/resubmit")
def resubmit_rejected_batch(batch_id: int, db=Depends(get_db), user=Depends(require_roles("FARMER"))):
    return submit_batch(db, batch_id, farmer_id=user["id"], resubmit=True)


@router.post("/{batch_id}/qr")
def create_batch_qr(batch_id: int, db=Depends(get_db), user=Depends(require_roles("AUDITOR"))):
    return create_qr_record(db, batch_id=batch_id, user_id=user["id"])


@router.patch("/{batch_id}/status")
def update_batch_status(batch_id: int, payload: BatchStatusUpdate, db=Depends(get_db), user=Depends(get_current_user)):
    raise HTTPException(status_code=400, detail="Status batch chỉ được thay đổi bởi Auditor approve/reject")
