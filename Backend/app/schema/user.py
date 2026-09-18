from typing import Optional
from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    id: int
    username: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    status: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str
    phone: Optional[str] = None
    role: str = "farmer"


class AuditorCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None


class UserStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(active|locked)$")
