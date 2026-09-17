
import sqlite3
import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..core.security import decode_access_token

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "db.db")
bearer_scheme = HTTPBearer(auto_error=False)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db=Depends(get_db)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Cần đăng nhập")
    claims = decode_access_token(credentials.credentials)
    row = db.execute(
        "SELECT id, username, full_name, role, status FROM users WHERE id = ?",
        (claims["sub"],),
    ).fetchone()
    if not row or row[4] != "active":
        raise HTTPException(status_code=401, detail="Tài khoản không hợp lệ hoặc đã bị khóa")
    return {"id": row[0], "username": row[1], "full_name": row[2], "role": row[3]}