import sqlite3
from fastapi import HTTPException
from ..schema.auth import RegisterRequest, LoginRequest
from ..services.hash_service import hash_password

def login_user(db, data: LoginRequest, expected_roles: list[str] | None = None):
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, username, password_hash, full_name, role, status
        FROM users
        WHERE email = ? OR username = ?
        """,
        (data.identifier, data.identifier),
    )
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Tài khoản hoặc mật khẩu không đúng")

    user_id, username, password_hash, full_name, role, status = row

    if status != "active":
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")

    if not verify_password(data.password, password_hash):
        raise HTTPException(status_code=401, detail="Tài khoản hoặc mật khẩu không đúng")

    if expected_roles and role not in expected_roles:
        raise HTTPException(status_code=403, detail="Tài khoản này không có quyền đăng nhập ở đây")

    return {
        "user_id": user_id,
        "username": username,
        "full_name": full_name,
        "role": role,
    }

def register_user_with_business(db: sqlite3.Connection, data: RegisterRequest):
    cursor = db.cursor()
    try:
        # Kiểm tra trùng email / tax_code trước khi insert
        cursor.execute("SELECT id FROM users WHERE email = ?", (data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email đã được sử dụng")

        cursor.execute("SELECT id FROM businesses WHERE tax_code = ?", (data.tax_code,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Mã số thuế đã tồn tại")

        password_hash = hash_password(data.password)

        # username: dùng email làm username, hoặc bạn có thể thêm field riêng
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, full_name, email, phone, role, status)
            VALUES (?, ?, ?, ?, ?, 'farmer', 'active')
            """,
            (data.email, password_hash, data.full_name, data.email, data.phone),
        )
        user_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO businesses (user_id, business_name, business_type, product_type, tax_code)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, data.business_name, data.business_type, data.product_type, data.tax_code),
        )
        business_id = cursor.lastrowid

        db.commit()
        return user_id, business_id

    except sqlite3.IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Lỗi ràng buộc dữ liệu: {e}")
    except Exception:
        db.rollback()
        raise