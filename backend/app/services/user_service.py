from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserUpdate
from app.DAO.users_dao import UsersDAO
from app.core.errors import AppError
from app.core.transactions import commit_or_rollback


async def list_users_service(
        db: AsyncSession,
        current_user: User,
        name: str | None = None,
        email: str | None = None,
        sort_by: str | None = None,
) -> list[User]:
    users = await UsersDAO.list(db, name=name, email=email, sort_by=sort_by)
    if not users:
        raise AppError(code="NOT_FOUND", message="No user found", status_code=404)
    return users


async def get_user_service(db: AsyncSession, user_id: int) -> User:
    user = await UsersDAO.get_by_id(db, user_id)
    if not user:
        raise AppError(code="NOT_FOUND", message="User not found", status_code=404)
    return user


async def update_user_service(
        db: AsyncSession,
        user_id: int,
        payload: UserUpdate,
        current_user: User,
) -> User:
    user = await UsersDAO.get_by_id(db, user_id)
    if not user:
        raise AppError(code="NOT_FOUND", message="User not found", status_code=404)
    
    if user_id != current_user.id:
        raise AppError(code="FORBIDDEN", message="Not authorized to update this user", sstatus_code=403)
    
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(user, key, value)

    await commit_or_rollback(db)
    await db.refresh(user)
    return user
    

async def delete_user_service(
        db: AsyncSession,
        user_id: int,
        current_user: User,
) -> None:
    user = await UsersDAO.get_by_id(db, user_id)
    if not user:
        raise AppError(code="NOT_FOUND", message="User not found", status_code=404)
    
    if current_user.role != "admin" and user_id != current_user.id:
        raise AppError(code="FORBIDDEN", message="Not authorized to delete this user", status_code=403)
    
    await db.delete(user)
    await commit_or_rollback(db)
    