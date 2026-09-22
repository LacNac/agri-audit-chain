from fastapi import APIRouter, Depends
from ..dependencies.auth import get_db
from ..schema.auth import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from ..services.auth_service import register_user_with_business, login_user

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, db = Depends(get_db)):
    user_id, business_id = register_user_with_business(db, data)
    return RegisterResponse(
        user_id=user_id,
        business_id=business_id,
        username=data.email,
    )

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db = Depends(get_db)):
    result = login_user(db, data, expected_roles=["FARMER"])
    return LoginResponse(**result)

@router.post("/login-auditor", response_model=LoginResponse)
def login_auditor(data: LoginRequest, db = Depends(get_db)):
    result = login_user(db, data, expected_roles=["AUDITOR"])
    return LoginResponse(**result)

@router.post("/login-admin", response_model=LoginResponse)
def login_admin(data: LoginRequest, db = Depends(get_db)):
    result = login_user(db, data, expected_roles=["ADMIN"])
    return LoginResponse(**result)