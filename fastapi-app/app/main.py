from fastapi import FastAPI
from app.models import user
from app.models import books
from app.core.database import engine, Base
from app.routers.user import user_router
from app.routers.books import book_router


app = FastAPI(title="My FastAPI App")
app.include_router(user_router, prefix="/api/v1")
app.include_router(book_router, prefix="/api/v1")

@app.on_event("startup")
async def on_startup():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
