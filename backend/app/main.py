from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.models import user
from app.models import books
from app.core.database import engine, Base
from app.routers.user import user_router
from app.routers.books import book_router
from app.routers.auth import auth_router
from app.routers.library import library_router
from app.core.logging import setup_logging
from app.middlewares.request_context import RequestContextMiddleware
from app.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    app_error_handler,
    unhandled_exception_handler,
)
from app.core.errors import AppError

setup_logging(level="INFO")

app = FastAPI(title="My FastAPI App")
app.add_middleware(RequestContextMiddleware)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(user_router, prefix="/api/v1")
app.include_router(book_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(library_router, prefix="/api/v1")

@app.on_event("startup")
async def on_startup():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
