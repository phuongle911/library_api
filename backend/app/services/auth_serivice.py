from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    decode_token,
    hash_refresh_token,
    create_access_token,
    )
from app.core.transactions import commit_or_rollback
from app.DAO.refresh_token_dao import get_refresh_token_by_hash


async def user_signup(db: AsyncSession, email: str, password: str, role: str):
    result = await db.execute(select(User).where(User.email == email))
    existing_email = result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exist"
            )
    user = User(email=email, hashed_password=hash_password(password), role=role)
    db.add(user)
    await commit_or_rollback(db)
    await db.refresh(user)
    return user


async def user_login(db: AsyncSession, email: str, password: str) -> str:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return user.email


async def refresh_access_token(db: AsyncSession, refresh_token: str):
    decoded = decode_token(refresh_token)

    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    token_hash = hash_refresh_token(refresh_token)
    row = await get_refresh_token_by_hash(db, token_hash)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if row.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked",
        )

    if row.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    email = decoded["sub"]
    access_token = create_access_token({"sub": email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
