from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


def _required_text(value: str) -> str:
    if value is None:
        return None
    value = value.strip()
    if not value:
        raise ValueError("Giá trị không được để trống hoặc chỉ chứa khoảng trắng")
    return value


class SampleCreate(BaseModel):
    sample_id: Optional[str] = None
    batch_id: int = Field(..., gt=0)
    sampling_date: Optional[date] = None
    sample_quantity: float = Field(..., gt=0)
    sample_unit: str = Field(..., min_length=1, max_length=50)
    sampling_location: str = Field(..., min_length=2, max_length=255)
    sampling_method: str = Field(..., min_length=2, max_length=255)
    status: str = "PENDING"

    _trim_required_text = field_validator("sample_unit", "sampling_location", "sampling_method", mode="before")(_required_text)
    _trim_optional_sample_id = field_validator("sample_id", mode="before")(_required_text)


class SampleOut(BaseModel):
    id: int
    sample_id: str
    sample_code: str
    batch_id: int
    sampling_date: Optional[date] = None
    sample_quantity: float
    sample_unit: str
    sampling_location: str
    sampling_method: str
    status: str = "PENDING"
