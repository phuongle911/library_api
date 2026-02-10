import logging
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.request")

REQUEST_ID_HEADER = "X-Request-Id"

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        start = time.perf_counter()

        #store on request.state (so deps/services can access if needed)
        request.state.request_id = request_id

        try:
            response: Response = await call_next(request)
            return response
        finally:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            status_code = getattr(locals().get("response"), "status_code", 500)

            #return request id back to client
            if "response" in locals():
                locals()["response"].headers[REQUEST_ID_HEADER] = request_id

                logger.info(
                    "http_request",
                    extra={
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "latency_ms": latency_ms,
                        "ip": request.client.host if request.client else None,
                           },
                )
