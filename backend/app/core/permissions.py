from fastapi import Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.models.user import User


def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user",)
    return current_user


def require_admin(current_user: User = Depends(require_active_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required",)
    return current_user


def is_admin(user: User) -> bool:
    return user.role == "admin"


def forbid(detail: str = "Forbidden"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def require_owner_or_admin(user: User, owner_id: int) -> None:
    if is_admin(user):
        return
    if user.id != owner_id:
        forbid("Not allowed")
        

