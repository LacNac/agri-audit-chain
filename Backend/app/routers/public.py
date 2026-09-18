from fastapi import APIRouter, Depends, HTTPException

from ..dependencies.auth import get_db

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/trace/{batch_code}")
def trace_batch(batch_code: str, db=Depends(get_db)):
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

    batch_id, _, product_name, origin, production_date, audit_status, farmer_id, farmer_name = batch_row
    report_rows = db.execute(
        """
        SELECT lr.result, lr.file_hash, lr.report_code
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
        verification = {
            "sha256": latest_hash,
            "integrity_proof": "sha256-present" if latest_hash else "missing",
            "verified": bool(latest_hash),
        }
    else:
        result_summary = {"report_count": 0, "latest_result": None, "latest_report_code": None}
        verification = {"sha256": None, "integrity_proof": "missing", "verified": False}

    return {
        "product_name": product_name,
        "origin": origin,
        "farmer": farmer_name or ("Farmer ID " + str(farmer_id) if farmer_id is not None else None),
        "production_date": production_date,
        "audit_status": audit_status,
        "laboratory_result_summary": result_summary,
        "verification": verification,
    }
