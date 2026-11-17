from fastapi import APIRouter, Depends, HTTPException
from ..core.security import create_access_token, decode_access_token
from ..dependencies.auth import get_db
from ..schema.auth import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse, RefreshRequest
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


@router.post("/refresh", response_model=LoginResponse)
def refresh_token(data: RefreshRequest, db=Depends(get_db)):
    claims = decode_access_token(data.access_token)
    row = db.execute(
        "SELECT id, username, full_name, role, status FROM users WHERE id = ?",
        (claims["sub"],),
    ).fetchone()
    if not row or row[4] != "active":
        raise HTTPException(status_code=401, detail="Tài khoản không hợp lệ hoặc đã bị khóa")
    return LoginResponse(
        user_id=row[0], username=row[1], full_name=row[2], role=row[3],
        access_token=create_access_token(row[0], row[3]), token_type="bearer",
    )


@router.post("/logout")
def logout():
    return {"success": True, "message": "Đã đăng xuất; client cần xóa access token"}