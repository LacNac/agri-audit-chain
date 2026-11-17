import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException

from ..dependencies.auth import get_db
from ..services.batch_service import get_batch_by_code, list_batches
from ..services.cold_chain_service import serialize_batch_for_cold_chain

router = APIRouter(prefix="/integration/batches", tags=["integration"])


def require_integration_key(
    x_integration_key: str | None = Header(default=None),
) -> None:
    expected_key = os.getenv("COLD_CHAIN_INTEGRATION_SECRET", "").strip()
    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="API tích hợp chưa được cấu hình",
        )
    if not x_integration_key or not hmac.compare_digest(x_integration_key, expected_key):
        raise HTTPException(status_code=401, detail="Integration key không hợp lệ")


@router.get("", dependencies=[Depends(require_integration_key)])
def list_transport_batches(db=Depends(get_db)):
    batches = list_batches(db)
    return {
        "success": True,
        "data": [
            serialize_batch_for_cold_chain(batch)
            for batch in batches
            if (batch.get("status") or "").upper() == "AUDITED"
        ],
    }


@router.get("/{batch_code}", dependencies=[Depends(require_integration_key)])
def get_transport_batch(batch_code: str, db=Depends(get_db)):
    batch = get_batch_by_code(db, batch_code)
    if (batch.get("status") or "").upper() != "AUDITED":
        raise HTTPException(
            status_code=409,
            detail="Batch chưa được Auditor phê duyệt để vận chuyển",
        )
    return {"success": True, "data": serialize_batch_for_cold_chain(batch)}
