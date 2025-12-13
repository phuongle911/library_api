from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_serivice import user_login, user_signup

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/signup")
async def signup(payload: UserCreate, db: AsyncSession=Depends(get_db)):
    user = await user_signup(db, payload.email, payload.password)
    return {"id": user.id, "email": user.email}


@auth_router.post("/login")
async def login(payload: UserLogin, db: AsyncSession=Depends(get_db)):
    token = await user_login(db, payload.email, payload.password)
    return {"access_token": token,
            "token_type": "bearer"}
