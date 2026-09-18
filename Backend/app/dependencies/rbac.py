from fastapi import Depends, HTTPException

from ..core.security import ALLOWED_ROLES, normalize_role
from .auth import get_current_user, get_db


def require_roles(*allowed_roles: str):
    allowed = {normalize_role(role) for role in allowed_roles}

    def checker(user=Depends(get_current_user)):
        if normalize_role(user["role"]) not in allowed:
            raise HTTPException(status_code=403, detail="Bạn không có quyền truy cập chức năng này")
        return user

    return checker


def require_permission(permission_code: str):
    def checker(user=Depends(get_current_user), db=Depends(get_db)):
        role_name = normalize_role(user["role"])
        if role_name not in ALLOWED_ROLES:
            raise HTTPException(status_code=403, detail="Vai trò không hợp lệ")

        row = db.execute(
            """
            SELECT 1 FROM role_permissions rp
            JOIN roles r ON r.id = rp.role_id
            JOIN permissions p ON p.id = rp.permission_id
            WHERE UPPER(r.code) = ? AND UPPER(p.code) = ?
            """,
            (role_name, permission_code.upper()),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=403, detail="Bạn không có quyền thực hiện thao tác này")
        return user

    return checker
