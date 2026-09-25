from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


def _required_text(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Giá trị không được để trống hoặc chỉ chứa khoảng trắng")
    return value

class RegisterRequest(BaseModel):
    # Thông tin tài khoản
    full_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=10, pattern=r"0[0-9]{9}")
    email: EmailStr = Field(
        ...,
        max_length=254,
        pattern=r"[a-zA-Z0-9._%+\-]+@gmail\.com$",
    )
    password: str = Field(..., min_length=6)

    # Thông tin doanh nghiệp
    business_name: str = Field(..., min_length=1, max_length=200)
    business_type: Literal[
        "Hộ kinh doanh cá thể",
        "Doanh nghiệp tư nhân",
        "Công ty TNHH",
        "Công ty Cổ phần",
        "Hợp tác xã",
    ]
    product_type: str = Field(..., min_length=1, max_length=100)
    tax_code: str = Field(
        ...,
        min_length=10,
        max_length=13,
        pattern=r"([0-9]{10}|[0-9]{13})",
    )

    _trim_required_text = field_validator("full_name", "phone", "password", "business_name", "business_type", "product_type", "tax_code", mode="before")(_required_text)

class RegisterResponse(BaseModel):
    user_id: int
    business_id: int
    username: str
    message: str = "Đăng ký thành công"

class LoginRequest(BaseModel):
    identifier: str   # email (doanh nghiệp) hoặc username (kiểm định)
    password: str

    _trim_required_text = field_validator("identifier", "password", mode="before")(_required_text)


class RefreshRequest(BaseModel):
    access_token: str

class LoginResponse(BaseModel):
    user_id: int
    username: str
    full_name: str
    role: str
    access_token: str
    token_type: str = "bearer"
    message: str = "Đăng nhập thành công"