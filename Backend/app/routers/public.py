from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from ..dependencies.auth import get_db

router = APIRouter(prefix="/public", tags=["public"])
UPLOADS_DIRS = (
    Path(__file__).resolve().parents[2] / "uploads",
    Path(__file__).resolve().parents[1] / "uploads",
)


def _trace_batch(batch_code: str, db):
    batch_row = db.execute(
        """
        SELECT b.id, b.batch_code, b.product_name, b.origin, b.production_date, b.status, b.farmer_id,
               u.full_name AS farmer_name
        FROM batches b
        LEFT JOIN users u ON u.id = b.farmer_id
        WHERE b.batch_code = ?
        """,
        (batch_code,),
    ).fetchone()
    if not batch_row:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    batch_id, resolved_batch_code, product_name, origin, production_date, audit_status, farmer_id, farmer_name = batch_row
    if audit_status != "AUDITED":
        raise HTTPException(status_code=403, detail="Batch chưa được kiểm định công khai")
    report_rows = db.execute(
        """
        SELECT lr.result, lr.file_hash, lr.report_code, lr.file_name
        FROM lab_reports lr
        JOIN samples s ON s.id = lr.sample_id
        WHERE s.batch_id = ?
        ORDER BY lr.id DESC
        """,
        (batch_id,),
    ).fetchall()

    if report_rows:
        latest_result = report_rows[0][0]
        latest_hash = report_rows[0][1]
        report_count = len(report_rows)
        result_summary = {
            "report_count": report_count,
            "latest_result": latest_result,
            "latest_report_code": report_rows[0][2],
        }
        reports = [
            {
                "name": row[3] or row[2] or "Phiếu kiểm nghiệm.pdf",
                "url": f"/public/trace/{resolved_batch_code}/report-file",
            }
            for row in report_rows
        ]
        verification = {
            "sha256": latest_hash,
            "integrity_proof": "sha256-present" if latest_hash else "missing",
            "verified": bool(latest_hash),
        }
    else:
        result_summary = {"report_count": 0, "latest_result": None, "latest_report_code": None}
        reports = []
        verification = {"sha256": None, "integrity_proof": "missing", "verified": False}

    trace_row = db.execute(
        "SELECT trace_id, public_url FROM trace_records WHERE batch_id = ? ORDER BY id DESC LIMIT 1",
        (batch_id,),
    ).fetchone()

    return {
        "batch_code": resolved_batch_code,
        "product_name": product_name,
        "origin": origin,
        "farmer": farmer_name or ("Farmer ID " + str(farmer_id) if farmer_id is not None else None),
        "production_date": production_date,
        "audit_status": audit_status,
        "laboratory_result_summary": result_summary,
        "reports": reports,
        "verification": verification,
        "trace_id": trace_row[0] if trace_row else None,
        "public_url": trace_row[1] if trace_row else None,
    }


@router.get("/trace/{batch_code}")
def trace_batch(batch_code: str, db=Depends(get_db)):
    return _trace_batch(batch_code, db)


@router.get("/trace-id/{trace_id}")
def trace_by_id(trace_id: str, db=Depends(get_db)):
    row = db.execute(
        "SELECT b.batch_code FROM trace_records t JOIN batches b ON b.id = t.batch_id WHERE t.trace_id = ?",
        (trace_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Mã QR không tồn tại")
    return _trace_batch(row[0], db)


@router.get("/trace/{batch_code}/report-file")
def get_public_report_file(batch_code: str, db=Depends(get_db)):
    batch = db.execute(
        "SELECT id, status FROM batches WHERE batch_code = ?",
        (batch_code,),
    ).fetchone()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")
    if batch[1] != "AUDITED":
        raise HTTPException(status_code=403, detail="Batch chưa được kiểm định công khai")

    report = db.execute(
        "SELECT file_name, file_path FROM lab_reports WHERE batch_id = ? ORDER BY id DESC LIMIT 1",
        (batch[0],),
    ).fetchone()
    if not report:
        raise HTTPException(status_code=404, detail="Batch chưa có report")

    file_name, file_path = report
    requested_name = Path(file_path or file_name or "").name
    report_path = next(
        (
            upload_dir / requested_name
            for upload_dir in UPLOADS_DIRS
            if (upload_dir / requested_name).resolve().parent == upload_dir.resolve()
            and (upload_dir / requested_name).is_file()
        ),
        None,
    )
    if report_path is None:
        raise HTTPException(status_code=404, detail="File report không tồn tại")
    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename=file_name or requested_name,
    )
