from pydantic import BaseModel, EmailStr, Field, field_validator


def _required_text(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Giá trị không được để trống hoặc chỉ chứa khoảng trắng")
    return value

class RegisterRequest(BaseModel):
    # Thông tin tài khoản
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=9, max_length=15)
    email: EmailStr
    password: str = Field(..., min_length=6)

    # Thông tin doanh nghiệp
    business_name: str
    business_type: str
    product_type: str
    tax_code: str = Field(..., min_length=10, max_length=14)

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