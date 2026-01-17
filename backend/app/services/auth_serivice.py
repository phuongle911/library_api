from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token


async def user_signup(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    existing_email = result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist")
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def user_login(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    print(user)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    token = create_access_token({"sub": user.email})
    return token
  