from fastapi import APIRouter, Depends, HTTPException
from ..dependencies.auth import get_db

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/trace/{batch_code}")
def trace_batch(batch_code: str, db=Depends(get_db)):
    row = db.execute("SELECT * FROM batches WHERE batch_code = ?", (batch_code,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Batch không tồn tại")

    columns = [col[1] for col in db.execute("PRAGMA table_info(batches)").fetchall()]
    return dict(zip(columns, row))
