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


class BatchCreate(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=200)
    product_type: str = Field(..., min_length=2, max_length=200)
    origin: str = Field(..., min_length=2, max_length=200)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    note: Optional[str] = None
    producer_name: Optional[str] = None
    farmer_id: Optional[int] = Field(default=None, exclude=True)

    _trim_required_text = field_validator("product_name", "product_type", "origin", "unit", mode="before")( _required_text)


class BatchUpdate(BaseModel):
    product_name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    product_type: Optional[str] = Field(default=None, min_length=2, max_length=200)
    origin: Optional[str] = Field(default=None, min_length=2, max_length=200)
    quantity: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = Field(default=None, min_length=1, max_length=50)
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    note: Optional[str] = None

    _trim_optional_text = field_validator("product_name", "product_type", "origin", "unit", mode="before")( _required_text)


class BatchOut(BaseModel):
    id: int
    batch_code: str
    product_name: str
    product_type: Optional[str] = None
    producer_name: Optional[str] = None
    origin: str
    quantity: float
    unit: str
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: str
    farmer_id: Optional[int] = None
    note: Optional[str] = None


class BatchStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None
