from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ..dependencies.auth import get_db
from ..dependencies.rbac import require_permission
from ..schema.audit import AuditDecision, LabReportCreate, LabReportOut
from ..services.audit_service import approve_batch, create_report, reject_batch

router = APIRouter(prefix="/auditor", tags=["auditor"])


@router.post("/reports", response_model=LabReportOut)
async def create_lab_report_with_file(
    sample_id: int = Form(...),
    batch_id: int = Form(...),
    lab_name: str = Form(...),
    lab_code: str = Form(...),
    report_date: date | None = Form(None),
    result: str = Form(...),
    file: UploadFile = File(...),
    file_path: str | None = Form(None),
    db=Depends(get_db),
    user=Depends(require_permission("AUDIT_VIEW")),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file PDF")

    pdf_bytes = await file.read()
    report = create_report(
        db,
        {
            "sample_id": sample_id,
            "batch_id": batch_id,
            "lab_name": lab_name,
            "lab_code": lab_code,
            "report_date": report_date,
            "result": result,
            "file_name": file.filename,
            "file_path": file_path,
        },
        file_bytes=pdf_bytes,
    )
    return LabReportOut(
        id=report["id"],
        report_code=report["report_code"],
        sample_id=sample_id,
        batch_id=batch_id,
        lab_name=lab_name,
        lab_code=lab_code,
        report_date=report_date,
        result=result,
        file_name=file.filename,
        file_hash=report["file_hash"],
        file_path=file_path or report["file_path"],
        status=report["status"],
    )


@router.post("/report", response_model=LabReportOut)
def create_lab_report_legacy(payload: LabReportCreate, db=Depends(get_db), user=Depends(require_permission("AUDIT_VIEW"))):
    if payload.file_hash:
        raise HTTPException(status_code=400, detail="Hash PDF không được nhập thủ công; hệ thống tự tính từ file upload")
    result = create_report(db, payload.model_dump(exclude_none=True), file_bytes=b"")
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
        file_hash=result["file_hash"],
        file_path=payload.file_path,
        status=result["status"],
    )


@router.post("/batches/{batch_id}/approve")
def approve(batch_id: int, payload: AuditDecision, db=Depends(get_db), user=Depends(require_permission("AUDIT_APPROVE"))):
    return approve_batch(db, batch_id, user_id=user["id"], reason=payload.reason)


@router.post("/batches/{batch_id}/reject")
def reject(batch_id: int, payload: AuditDecision, db=Depends(get_db), user=Depends(require_permission("AUDIT_REJECT"))):
    return reject_batch(db, batch_id, user_id=user["id"], reason=payload.reason or "Không đạt tiêu chuẩn")
