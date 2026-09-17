from fastapi import APIRouter, Depends
from ..dependencies.auth import get_db
from ..dependencies.rbac import require_permission
from ..schema.audit import AuditDecision, LabReportCreate, LabReportOut
from ..services.audit_service import approve_batch, create_report, reject_batch

router = APIRouter(prefix="/auditor", tags=["auditor"])


@router.post("/report", response_model=LabReportOut)
def create_lab_report(payload: LabReportCreate, db=Depends(get_db), user=Depends(require_permission("AUDIT_VIEW"))):
    result = create_report(db, payload.model_dump())
    return LabReportOut(
        id=result["id"],
        report_code=result["report_code"],
        sample_id=payload.sample_id,
        batch_id=payload.batch_id,
        lab_name=payload.lab_name,
        lab_code=payload.lab_code,
        report_date=payload.report_date,
        result=payload.result,
        file_name=payload.file_name,
        file_hash=payload.file_hash,
        file_path=payload.file_path,
        status=result["status"],
    )


@router.post("/batches/{batch_id}/approve")
def approve(batch_id: int, payload: AuditDecision, db=Depends(get_db), user=Depends(require_permission("AUDIT_APPROVE"))):
    return approve_batch(db, batch_id, user_id=user["id"], reason=payload.reason)


@router.post("/batches/{batch_id}/reject")
def reject(batch_id: int, payload: AuditDecision, db=Depends(get_db), user=Depends(require_permission("AUDIT_REJECT"))):
    return reject_batch(db, batch_id, user_id=user["id"], reason=payload.reason or "Không đạt tiêu chuẩn")
