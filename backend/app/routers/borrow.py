from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.borrow import BorrowBookRequest, BorrowRecordResponse
from app.services.borrow_service import borrow_book_service


borrow_router = APIRouter(prefix="/borrow", tags=["Borrow"])


@borrow_router.post("/books/{book_id}", response_model=BorrowRecordResponse)
async def borrow_book(
    book_id: int,
    payload: BorrowBookRequest,
    db: AsyncSession = Depends(get_db),
):
    return await borrow_book_service(
        db=db,
        book_id=book_id,
        user_id=payload.user_id,
    )