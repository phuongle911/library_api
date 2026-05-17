from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import HTTPException, status
import hashlib
import os

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
             )
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY


def _prehash(password: str) -> str:
    # fixed-length string (64 hex chars)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    return pwd_context.hash(_prehash(password))


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_prehash(password), hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": datetime.now(timezone.utc) + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                ),
            "type": "access"
            }
            )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": datetime.now(timezone.utc) + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
                ),
            "type": "refresh",
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],)
        return payload
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
            )


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def refresh_token_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
