from functools import wraps
from typing import Callable, Awaitable, Any, Type
import asyncio

def retry_async(
        attempts: int = 3,
        delay_seconds: float = 0.25,
        exceptions: tuple[Type[BaseException], ...] = (Exception,),
):
    def decorator(fn: Callable[..., Awaitable[Any]]):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            last_err: BaseException | None = None
            for i in range(attempts):
                try:
                    return await fn(*args, **kwargs)
                except exceptions as e:
                    last_err = e
                    if i == attempts - 1:
                        raise
                    await asyncio.sleep(delay_seconds * (2 ** i))
            raise last_err
        return wrapper
    return decorator