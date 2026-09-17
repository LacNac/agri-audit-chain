from fastapi import APIRouter, Depends

from ..dependencies.auth import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_current_user(db=Depends(get_db)):
	return {"message": "User profile endpoint is ready", "users": db.execute("SELECT id, username, full_name, email, role FROM users ORDER BY id").fetchall()}


@router.get("")
def list_users(db=Depends(get_db)):
	rows = db.execute("SELECT id, username, full_name, email, role, status FROM users ORDER BY id").fetchall()
	return [{
		"id": row[0],
		"username": row[1],
		"full_name": row[2],
		"email": row[3],
		"role": row[4],
		"status": row[5],
	} for row in rows]
