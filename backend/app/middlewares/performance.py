import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)

        duration = time.perf_counter() - start

        logger.info(
            "request_completed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "duration_ms": round(duration * 1000, 2),
                "status_code": response.status_code,
            },
        )

        return response