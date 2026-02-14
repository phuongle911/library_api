from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User


class UsersDAO:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    
    @staticmethod
    async def list (
        db: AsyncSession, 
        name: str | None = None,
        email: str | None = None,
        sort_by: str | None = None,
        limit: int = 50, 
        offset: int = 0,
        ) -> list[User]:
        q = select(User)

        if name:
            q = q.where(User.name.ilike(f"%{name}%"))
        if email:
            q = q.where(User.email.ilike(f"{email}%"))
        if sort_by == "name":
            q = q.order_by(User.name.asc())
        elif sort_by == "email":
            q = q.order_by(User.email.asc())
        elif sort_by == "oldest":
            q = q.order_by(User.id.asc())
        else: # newest/default
            q = q.order_by(User.id.desc())

        q = q.offset(offset).limit(limit)

        res = await db.execute(q)
        return list(res.scalars().all())

    
    @staticmethod
    async def create(db: AsyncSession, user: User) -> User:
        db.add(user)
        return user
    
    @staticmethod
    async def set_role(db: AsyncSession, user: User, role: str) -> User:
        user.role = role
        db.add(user)
        return user