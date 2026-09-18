from fastapi import APIRouter, Depends, HTTPException

from ..dependencies.auth import get_current_user, get_db
from ..dependencies.rbac import require_roles

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_current_user_profile(db=Depends(get_db), user=Depends(get_current_user)):
    row = db.execute(
        "SELECT id, full_name, email, phone, role, status FROM users WHERE id = ?",
        (user["id"],),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    business_row = db.execute(
        "SELECT id, business_name, business_type, product_type, tax_code FROM businesses WHERE user_id = ?",
        (user["id"],),
    ).fetchone()

    payload = {
        "user_id": row[0],
        "full_name": row[1],
        "email": row[2],
        "phone": row[3],
        "role": row[4],
        "status": row[5],
        "business": None,
    }

    if business_row:
        payload["business"] = {
            "business_id": business_row[0],
            "business_name": business_row[1],
            "business_type": business_row[2],
            "product_type": business_row[3],
            "tax_code": business_row[4],
        }

    return payload


@router.get("")
def list_users(db=Depends(get_db), user=Depends(require_roles("ADMIN"))):
    if user and str(user.get("role", "")).upper() != "ADMIN":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem toàn bộ người dùng")

    rows = db.execute(
        "SELECT id, full_name, email, role, status FROM users ORDER BY id"
    ).fetchall()
    return [{
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "role": row[3],
        "status": row[4],
    } for row in rows]
