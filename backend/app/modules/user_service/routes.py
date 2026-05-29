from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, RefreshTokenSchema
from app.services.auth_serivice import user_login, user_signup, refresh_access_token
from app.core.security import (
  create_access_token,
  create_refresh_token,
  hash_refresh_token,
  refresh_token_expires_at,
  decode_token
)
from app.DAO.refresh_token_dao import (
    create_refresh_token_row,
    get_refresh_token_by_hash,
    revoke_refresh_token
    )
from app.models.user import User
from sqlalchemy import select

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/signup")
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await user_signup(db, payload.email, payload.password, payload.role)
    return {"id": user.id, "email": user.email}


@auth_router.post("/login")
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    email = await user_login(db, payload.email, payload.password)
    # fetch user to get user_id
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one()
    access_token = create_access_token({"sub": email})
    refresh_token = create_refresh_token({"sub": email})
    await create_refresh_token_row(
        db=db,
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=refresh_token_expires_at(),
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@auth_router.post("/login/refresh")
async def refresh(
    payload: RefreshTokenSchema,
    db: AsyncSession = Depends(get_db)
      ):
    
    return await refresh_access_token(db, payload.refresh_token)
   

@auth_router.post("/logout")
async def logout(payload: RefreshTokenSchema, db: AsyncSession = Depends(get_db)):
    token_hash = hash_refresh_token(payload.refresh_token)
    row = await get_refresh_token_by_hash(db, token_hash)
    if not row:
        return {"message": "Already logged out"}
    if row.revoked_at is None:
        await revoke_refresh_token(db, token_hash)
        return {"message": "Logged out successfully"}
