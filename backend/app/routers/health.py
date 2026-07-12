import socket
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db


health_router = APIRouter(tags=["Health"])


@health_router.get("ready")
async def ready(db: AsyncSession = Depends(get_db)):

    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
        }
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILBLE,
            detail="Database unavailable",
        )

@health_router.get("/health")
async def health():
    return {
        "status": "ok",
        "host": socket.gethostname(),
        }
