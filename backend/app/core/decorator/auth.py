from functools import wraps
from typing import Callable, Any, Awaitable
from fastapi import Request, HTTPException, status
from app.core.security import decode_token


def require_auth(fn: Callable[..., Awaitable[Any]]):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        request: Request | None = kwargs.get("request")

        if request is None:
            for a in args:
                if isinstance(a, Request):
                    request = a
                    break

        if request is None:
            raise RuntimeError("request: Reuest is required")

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Bearer token",
            )

        token = auth.split(" ", 1)[1].strip()
        try:
            payload = decode_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        request.state.user = payload
        return await fn(*args, **kwargs)

    return wrapper
