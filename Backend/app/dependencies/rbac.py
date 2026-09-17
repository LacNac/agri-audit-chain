from fastapi import Depends, HTTPException

from .auth import get_current_user, get_db


def require_permission(permission_code: str):
	def checker(user=Depends(get_current_user), db=Depends(get_db)):
		row = db.execute(
			"""
			SELECT 1 FROM role_permissions rp
			JOIN roles r ON r.id = rp.role_id
			JOIN permissions p ON p.id = rp.permission_id
			WHERE r.code = ? AND p.code = ?
			""",
			(user["role"], permission_code),
		).fetchone()
		if not row:
			raise HTTPException(status_code=403, detail="Bạn không có quyền thực hiện thao tác này")
		return user

	return checker
