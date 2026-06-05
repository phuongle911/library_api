from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as http_status

from app.infrastructure.repositories.book_repository import BookRepository
from app.core.database import get_db
from app.internal.auth import verify_internal_token


internal_router = APIRouter(
    prefix="/internal/books", tags=["Internal Books"],
    dependencies = [Depends(verify_internal_token)],
    )

@internal_router.get("/{book_id}")
async def get_book_internal(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    book = await BookRepository.get_by_id(db, book_id)

    if not book:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    return {
        "id": book.id,
        "title": book.title,
        "available_copies": book.available_copies,
    }
