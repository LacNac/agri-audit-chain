import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from ..core.security import hash_password
from ..dependencies.auth import get_current_user, get_db
from ..dependencies.rbac import require_roles
from ..schema.user import AuditorCreate, UserCreate, UserRoleUpdate, UserStatusUpdate, UserUpdate

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


@router.get("/{user_id}")
def get_user(user_id: int, db=Depends(get_db), user=Depends(require_roles("ADMIN"))):
    row = db.execute(
        "SELECT id, username, full_name, email, phone, role, status, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    return dict(zip(("id", "username", "full_name", "email", "phone", "role", "status", "created_at"), row))


@router.post("", status_code=201)
def create_user(data: UserCreate, db=Depends(get_db), user=Depends(require_roles("ADMIN"))):
    role = data.role.upper()
    if role not in {"ADMIN", "FARMER", "AUDITOR", "PUBLIC"}:
        raise HTTPException(status_code=400, detail="Role không hợp lệ")
    try:
        cursor = db.execute(
            "INSERT INTO users (username, password_hash, full_name, email, phone, role, status) VALUES (?, ?, ?, ?, ?, ?, 'active')",
            (data.username, hash_password(data.password), data.full_name, data.email, data.phone, role),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username hoặc email đã tồn tại")
    return get_user(cursor.lastrowid, db, user)


@router.patch("/{user_id}")
def update_user(user_id: int, data: UserUpdate, db=Depends(get_db), user=Depends(require_roles("ADMIN"))):
    updates = data.model_dump(exclude_none=True)
    if "role" in updates:
        updates["role"] = updates["role"].upper()
        if updates["role"] not in {"ADMIN", "FARMER", "AUDITOR", "PUBLIC"}:
            raise HTTPException(status_code=400, detail="Role không hợp lệ")
    if not updates:
        return get_user(user_id, db, user)
    if not db.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone():
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    assignments = ", ".join(f"{field} = ?" for field in updates)
    try:
        db.execute(f"UPDATE users SET {assignments} WHERE id = ?", [*updates.values(), user_id])
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email đã tồn tại")
    return get_user(user_id, db, user)


@router.patch("/{user_id}/role")
def update_user_role(user_id: int, data: UserRoleUpdate, db=Depends(get_db), user=Depends(require_roles("ADMIN"))):
    return update_user(user_id, UserUpdate(role=data.role), db, user)


@router.post("/auditors", status_code=201)
def create_auditor(data: AuditorCreate, db=Depends(get_db), user=Depends(require_roles("ADMIN"))):
    username = data.email.split("@", 1)[0].strip()
    if not username:
        raise HTTPException(status_code=400, detail="Email không hợp lệ")

    try:
        cursor = db.execute(
            """
            INSERT INTO users (username, password_hash, full_name, email, phone, role, status)
            VALUES (?, ?, ?, ?, ?, 'AUDITOR', 'active')
            """,
            (username, hash_password(data.password), data.full_name.strip(), data.email.strip(), data.phone or ""),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email hoặc tên đăng nhập đã tồn tại")

    return {
        "id": cursor.lastrowid,
        "username": username,
        "full_name": data.full_name.strip(),
        "email": data.email.strip(),
        "phone": data.phone or "",
        "role": "AUDITOR",
        "status": "active",
    }


@router.patch("/{user_id}/status")
def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db=Depends(get_db),
    user=Depends(require_roles("ADMIN")),
):
    if user_id == user["id"] and data.status == "locked":
        raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản đang sử dụng")

    cursor = db.execute(
        "UPDATE users SET status = ? WHERE id = ?",
        (data.status, user_id),
    )
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    db.commit()
    return {"id": user_id, "status": data.status}
