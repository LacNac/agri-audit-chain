from fastapi import APIRouter, Depends
from ..dependencies.auth import get_db
from ..dependencies.rbac import require_permission

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
def dashboard(db=Depends(get_db), user=Depends(require_permission("DASHBOARD_VIEW"))):
    return {
        "total_batches": db.execute("SELECT COUNT(*) FROM batches").fetchone()[0],
        "total_users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "total_reports": db.execute("SELECT COUNT(*) FROM lab_reports").fetchone()[0],
        "status_summary": {
            "UNVERIFIED": db.execute("SELECT COUNT(*) FROM batches WHERE status = 'UNVERIFIED'").fetchone()[0],
            "AUDITED": db.execute("SELECT COUNT(*) FROM batches WHERE status = 'AUDITED'").fetchone()[0],
            "REJECTED": db.execute("SELECT COUNT(*) FROM batches WHERE status = 'REJECTED'").fetchone()[0],
        },
    }
