import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import AppError, error_payload

logger = logging.getLogger("app.errors")


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    request_id = getattr(request.state, "request_id", None)
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        code = detail["code"]
        message = detail["message"]
    else:
        code = "HTTP_ERROR"
        message = detail if isinstance(detail, str) else "Request failed"

        logger.warning(
           "http_exception",
           extra={
               "request_id": request_id,
               "status_code": exc.status_code,
               "path": request.url.path,
               "error_code": code,
           },
        )

        return JSONResponse(
           status_code=exc.status_code,
           content=error_payload(code, message, request_id),
        )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    rid = getattr(request.state, "request_id", None)

    logger.warning(
        "validation_error",
        extra={"request_id": rid, "status_code": 422, "path": request.url.path},
    )
    return JSONResponse(
        status_code=422,
        content={"error": "VALIDATION_ERROR",
                 "message": "Invalid request paylaod",
                 "detail": exc.errors(),
                 "request_id": rid,
                 },
                 )


async def app_error_handler(request: Request, exc: AppError):
    rid = getattr(request.state, "request_id", None)

    logger.info(
        "app_error",
        extra={
            "request_id": rid,
            "status_code": exc.status_code,
            "path": request.url.path
            },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc.code, exc.message, rid),
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    rid = getattr(request.state, "request_id", None)

    logger.exception(
        "unhandled_exception",
        extra={"request_id": rid, "status_code": 500, "path": request.url.path},
    )
    return JSONResponse(
        status_code=500,
        content=error_payload("INTERNAL_SERVER_ERROR", "Something went wrong", rid),
    )
