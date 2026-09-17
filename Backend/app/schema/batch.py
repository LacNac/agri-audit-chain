from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class BatchCreate(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=200)
    producer_name: str = Field(..., min_length=2, max_length=200)
    origin: str = Field(..., min_length=2, max_length=200)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50)
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    farmer_id: Optional[int] = None


class BatchOut(BaseModel):
    id: int
    batch_code: str
    product_name: str
    producer_name: str
    origin: str
    quantity: float
    unit: str
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: str
    farmer_id: Optional[int] = None


class BatchStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None
