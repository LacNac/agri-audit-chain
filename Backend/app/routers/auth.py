from fastapi import APIRouter, Depends
from dependencies.auth import get_db
from schema.auth import RegisterRequest, RegisterResponse
from services.auth_service import register_user_with_business

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, db = Depends(get_db)):
    user_id, business_id = register_user_with_business(db, data)
    return RegisterResponse(
        user_id=user_id,
        business_id=business_id,
        username=data.email,
    )