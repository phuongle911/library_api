from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, RefreshTokenSchema
from app.core.security import create_access_token, decode_token, create_refresh_token
from app.services.auth_serivice import user_login, user_signup

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/signup")
async def signup(payload: UserCreate, db: AsyncSession=Depends(get_db)):
    user = await user_signup(db, payload.email, payload.password)
    print("Enpoint", user)
    return {"id": user.id, "email": user.email}


@auth_router.post("/login")
async def login(payload: UserLogin, db: AsyncSession=Depends(get_db)):
    email = await user_login(
        db,
        payload.email,
        payload.password
    )
    access_token = create_access_token({"sub": email})
    refresh_token = create_refresh_token({"sub":email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@auth_router.post("/login/refresh")
async def refresh(payload: RefreshTokenSchema):
    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    email = decoded["sub"]
    access_token = create_access_token({"sub": email})
    return {"access_token": access_token, "token_type": "bearer"}
