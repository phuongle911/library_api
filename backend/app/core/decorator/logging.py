from functools import wraps
from typing import Callable, Any, Awaitable
import time
import logging

logger = logging.getLogger("uvicorn.error")

def log_route(fn: Callable[..., Awaitable[Any]]):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            res = await fn(*args, **kwargs)
            ms = (time.perf_counter() - start) * 1000
            logger.info("route_ok", extra={"route": fn.__name__, "ms": round(ms, 2)})
            return res
        except Exception:
            ms = (time.perf_counter() - start) * 1000
            logger.exception("route_fail", extra={"route": fn.__name__, "ms": round(ms, 2)})
            raise
    
    return wrapper