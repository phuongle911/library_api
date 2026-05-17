from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


health_router = APIRouter(tags=["Health"])


@health_router.get("ready")
async def ready(db: AsyncSession = Depends(get_db)):

    await db.execute(text("SELECT 1"))
    return {
        "status": "ready",
        "database": "connected",
    }

@health_router.get("/health")
async def health():
    return {"status": "ok"}