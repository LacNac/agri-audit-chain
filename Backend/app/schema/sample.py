from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class SampleCreate(BaseModel):
    sample_code: Optional[str] = None
    sample_type: str = Field(..., min_length=2, max_length=200)
    collected_date: Optional[date] = None
    source_location: Optional[str] = None
    status: str = "PENDING"


class SampleOut(BaseModel):
    id: int
    sample_code: str
    batch_id: int
    sample_type: str
    collected_date: Optional[date] = None
    source_location: Optional[str] = None
    status: str
