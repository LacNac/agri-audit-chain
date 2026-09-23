from typing import Optional
from pydantic import BaseModel, Field, field_validator


def _required_text(value: str) -> str:
    if value is None:
        return None
    value = value.strip()
    if not value:
        raise ValueError("Giá trị không được để trống hoặc chỉ chứa khoảng trắng")
    return value


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

    _trim_required_text = field_validator("username", "password", "full_name", "email", mode="before")(_required_text)


class AuditorCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None

    _trim_required_text = field_validator("full_name", "email", "password", mode="before")(_required_text)


class UserStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(active|locked)$")


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None

    _trim_optional_text = field_validator("full_name", "email", "phone", "role", mode="before")(_required_text)


class UserRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(ADMIN|FARMER|AUDITOR|PUBLIC)$")
