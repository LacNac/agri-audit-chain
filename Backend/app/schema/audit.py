from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


def _required_text(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Giá trị không được để trống hoặc chỉ chứa khoảng trắng")
    return value


class LabReportOut(BaseModel):
    id: int
    report_code: str
    sample_id: int
    batch_id: int
    lab_name: str
    lab_code: str
    report_date: Optional[date] = None
    result: str
    file_name: Optional[str] = None
    file_hash: Optional[str] = None
    file_path: Optional[str] = None
    status: str
    proof_hash: Optional[str] = None
    proof_valid: Optional[bool] = None


class AuditDecision(BaseModel):
    reason: str = Field(..., min_length=1)

    _trim_reason = field_validator("reason", mode="before")(_required_text)
