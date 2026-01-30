from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, RefreshTokenSchema
from app.core.security import create_access_token, decode_token
from app.services.auth_serivice import user_login, user_signup

from app.core.security import (
  create_access_token,
  create_refresh_token,
  hash_refresh_token,
  refresh_token_expires_at,
)
from app.DAO.refresh_token_dao import create_refresh_token_row
from app.models.user import User
from sqlalchemy import select

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/signup")
async def signup(payload: UserCreate, db: AsyncSession=Depends(get_db)):
    user = await user_signup(db, payload.email, payload.password)
    print("Enpoint", user)
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
async def refresh(payload: RefreshTokenSchema):
    email = decode_token(payload.refresh_token)["sub"]
    access_token = create_access_token({"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}
