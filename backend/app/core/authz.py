from fastapi import Depends
from app.core.errors import AppError
from app.models.user import User
from app.core.dependencies import get_current_user


def require_roles(*roles: str):
    def dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise AppError(code="FORBIDDEN", message="You do not have permission", status_code=403)
        return current_user
    return dep