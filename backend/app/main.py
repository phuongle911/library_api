import logging
import sentry_sdk
import os
from sentry_sdk.integrations.fastapi import FastApiIntegration
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models import user
from app.models import books
from app.core.database import engine, Base
from app.routers.user import user_router
from app.routers.books import book_router
from app.routers.auth import auth_router
from app.routers.library import library_router
from app.routers.categories import category_router
from app.routers.borrow import borrow_router
from app.routers.job import job_router
#from app.core.logging import setup_logging
from app.core.logging_config import setup_logging
from app.core.request_id import set_request_id, generate_request_id, get_request_id
from app.middlewares.request_context import RequestContextMiddleware
from app.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    app_error_handler,
    unhandled_exception_handler,
)
from app.core.errors import AppError

setup_logging()
logger = logging.getLogger(__name__)
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DNS"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv("APP_ENV", "development"),
)

app = FastAPI(title="My FastAPI App")
app.add_middleware(RequestContextMiddleware)


app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(user_router, prefix="/api/v1")
app.include_router(book_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(library_router, prefix="/api/v1")
app.include_router(borrow_router, prefix="/api/v1")
app.include_router(job_router, prefix="/api/v1")

@app.on_event("startup")
async def on_startup():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("UNHANDLED_EXCEPTION")

    return JSONResponse(
        status_code = 500,
        content = {"error": "Internal Server Error", "message": str(exc), "request_id": get_request_id(),
                   },
    )