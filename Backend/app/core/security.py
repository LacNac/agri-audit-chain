import hashlib
import base64
import hmac
import json
import time

from fastapi import HTTPException


DEFAULT_PEPPER = "agri-audit-chain-v1"
JWT_SECRET = "agri-audit-chain-jwt-v1"
JWT_TTL_SECONDS = 3600


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password không được để trống")
    return hashlib.sha256(f"{DEFAULT_PEPPER}:{password}".encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    return hash_password(plain_password) == hashed_password


def _encode_segment(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode_segment(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(user_id: int, role: str) -> str:
    header = _encode_segment(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _encode_segment(json.dumps({"sub": str(user_id), "role": role, "exp": int(time.time()) + JWT_TTL_SECONDS}, separators=(",", ":")).encode())
    unsigned = f"{header}.{payload}".encode("ascii")
    signature = _encode_segment(hmac.new(JWT_SECRET.encode(), unsigned, hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def decode_access_token(token: str) -> dict:
    try:
        header, payload, signature = token.split(".")
        unsigned = f"{header}.{payload}".encode("ascii")
        expected = _encode_segment(hmac.new(JWT_SECRET.encode(), unsigned, hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid signature")
        data = json.loads(_decode_segment(payload))
        if int(data["exp"]) < int(time.time()):
            raise ValueError("expired token")
        return data
    except (KeyError, ValueError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")
