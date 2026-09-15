from pydantic import BaseModel, EmailStr, Field
from typing import Optional

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

class RegisterResponse(BaseModel):
    user_id: int
    business_id: int
    username: str
    message: str = "Đăng ký thành công"