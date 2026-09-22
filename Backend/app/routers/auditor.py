from datetime import date
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ..dependencies.auth import get_db
from ..dependencies.rbac import require_permission
from ..schema.audit import AuditDecision, LabReportCreate, LabReportOut
from ..services.audit_service import approve_batch, create_report, reject_batch

router = APIRouter(prefix="/auditor", tags=["auditor"])


@router.get("/queue")
def get_audit_queue(db=Depends(get_db), user=Depends(require_permission("AUDIT_VIEW"))):
    batches = db.execute(
        """
        SELECT b.id, b.batch_code, b.product_name, b.product_type, b.producer_name,
               b.origin, b.quantity, b.unit, b.production_date, b.expiry_date,
               b.status, b.created_at,
               (SELECT COUNT(*) FROM samples s WHERE s.batch_id = b.id) AS sample_count,
               (SELECT COUNT(*) FROM lab_reports lr WHERE lr.batch_id = b.id) AS report_count
        FROM batches b
        WHERE b.status IN ('UNVERIFIED', 'REJECTED')
        ORDER BY CASE b.status WHEN 'REJECTED' THEN 0 ELSE 1 END, b.id DESC
        """
    ).fetchall()

    queue = []
    for row in batches:
        batch = dict(zip(
            [
                "id", "batch_code", "product_name", "product_type", "producer_name",
                "origin", "quantity", "unit", "production_date", "expiry_date",
                "status", "created_at", "sample_count", "report_count",
            ],
            row,
        ))
        sample_columns = [column[1] for column in db.execute("PRAGMA table_info(samples)").fetchall()]
        batch["samples"] = [dict(zip(sample_columns, sample)) for sample in db.execute(
            "SELECT * FROM samples WHERE batch_id = ? ORDER BY id DESC", (batch["id"],)
        ).fetchall()]
        report_columns = [column[1] for column in db.execute("PRAGMA table_info(lab_reports)").fetchall()]
        batch["reports"] = [dict(zip(report_columns, report)) for report in db.execute(
            "SELECT * FROM lab_reports WHERE batch_id = ? ORDER BY id DESC", (batch["id"],)
        ).fetchall()]
        batch["latest_audit"] = db.execute(
            """
            SELECT action, old_value, new_value, created_at
            FROM audit_trails
            WHERE entity_type = 'batch' AND entity_id = ?
            ORDER BY id DESC LIMIT 1
            """,
            (batch["id"],),
        ).fetchone()
        if batch["latest_audit"]:
            action, old_value, new_value, created_at = batch["latest_audit"]
            old_data = json.loads(old_value) if old_value else {}
            new_data = json.loads(new_value) if new_value else {}
            batch["latest_audit"] = {
                "action": action,
                "previous_status": old_data.get("status"),
                "new_status": new_data.get("status"),
                "reason": new_data.get("reason"),
                "created_at": created_at,
            }
        queue.append(batch)

    return queue


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
