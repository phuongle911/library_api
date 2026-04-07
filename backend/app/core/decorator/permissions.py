from functools import wraps
from typing import Callable, Any, Awaitable
from fastapi import Request, HTTPException, status


def require_roles(*allowed_roles: str):
    def decorator(fn: Callable[..., Awaitable[Any]]):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            request: Request | None = kwargs.get("request")
            if request is None:
                for a in args:
                    if isinstance(a, Request):
                        request = a
                        break
                    if request is None:
                        raise RuntimeError(
                            "require_roles decorator needs 'request: "
                            "Request' in endpoint signature"
                            )

                    user = getattr(request.state, "user", None)
                    if not user:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not authenticated"
                            )

                    role = user.get("role")
                    if role not in allowed_roles:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden"
                            )

                    return await fn(*args, **kwargs)
                return wrapper
            return decorator
