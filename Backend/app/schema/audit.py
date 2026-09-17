from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class LabReportCreate(BaseModel):
    sample_id: int
    batch_id: int
    lab_name: str = Field(..., min_length=2, max_length=200)
    lab_code: str = Field(..., min_length=2, max_length=100)
    report_date: Optional[date] = None
    result: str = Field(..., min_length=2, max_length=100)
    file_name: Optional[str] = None
    file_hash: Optional[str] = None
    file_path: Optional[str] = None
    status: str = "PENDING"


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


class AuditDecision(BaseModel):
    reason: Optional[str] = None
