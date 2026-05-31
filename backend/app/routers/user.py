from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.core.database import get_db, get_read_db
from app.core.dependencies import get_current_user
from app.core.decorator.auth import require_auth
from app.core.decorator.logging import log_route
from app.core.transactions import commit_or_rollback
from app.core.auth import require_roles
from backend.app.modules.user_service.user_service import (
   list_users_service,
   get_user_service,
   update_user_service,
   delete_user_service,
)
from backend.app.modules.user_service.users_dao import UsersDAO
from app.core.errors import AppError


user_router = APIRouter()


class SetRolePayload(BaseModel):
    role: str


@user_router.get("/me")
@log_route
@require_auth
async def me(request: Request):
    return {"user": request.state.user}


@user_router.get("/users/", response_model=list[UserResponse], status_code=200)
async def list_users(
   name: str | None = None,
   email: str | None = None,
   sort_by: str | None = None,
   db: AsyncSession = Depends(get_read_db),
   current_user: User = Depends(get_current_user),
):
    return await list_users_service(
      db,
      current_user,
      name=name,
      email=email,
      sort_by=sort_by
      )


@user_router.get("/users/{user_id}", response_model=UserResponse, status_code=200)
async def get_user(
   user_id: int,
   db: AsyncSession = Depends(get_read_db),
   current_user: User = Depends(get_current_user),
):
    return await get_user_service(db, user_id, current_user)


@user_router.put("/users/{user_id}", response_model=UserResponse, status_code=200)
async def update_user(
   user_id: int,
   payload: UserUpdate,
   db: AsyncSession = Depends(get_db),
   current_user: User = Depends(get_current_user),
):
    return await update_user_service(db, user_id, payload, current_user)


@user_router.delete("/users/{user_id}", status_code=204)
async def delete_user(
   user_id: int,
   db: AsyncSession = Depends(get_db),
   current_user: User = Depends(get_current_user),
):
    await delete_user_service(db, user_id, current_user)
    return None


@user_router.patch("/users/{user_id}/role")
async def set_user_role(
   user_id: int,
   payload: SetRolePayload,
   db: AsyncSession = Depends(get_db),
   current_user: User = Depends(require_roles("admin")),
):
    # validate role
    if payload.role not in ("admin", "user"):
        raise AppError(code="VALIDATION_ERROR", message="Invalid role", status_code=400)

    user = await UsersDAO.get_by_id(db, user_id)
    if not user:
        raise AppError(code="NOT_FOUND", message="User not found", status_code=404)

    user.role = payload.role
    await commit_or_rollback(db)  # your transaction helper
    await db.refresh(user)

    return user
