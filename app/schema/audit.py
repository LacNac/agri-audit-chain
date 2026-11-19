from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


def _required_text(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Giá trị không được để trống hoặc chỉ chứa khoảng trắng")
    return value


def _optional_text(value: str | None) -> str | None:
    return _required_text(value) if value is not None else None


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
    return_goods: Optional[bool] = False

    _trim_reason = field_validator("reason", mode="before")(_required_text)


class AuditApproval(BaseModel):
    reason: str = Field(..., min_length=1)
    destination: Optional[str] = Field(default=None, min_length=2, max_length=300)

    _trim_reason = field_validator("reason", mode="before")(_required_text)
    _trim_destination = field_validator("destination", mode="before")(_optional_text)
