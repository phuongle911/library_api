from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.borrow import BorrowBookRequest, BorrowRecordResponse
from app.services.borrow_service import (
    borrow_book_service,
    get_active_borrows_service,
    get_borrow_history_service,
    get_user_borrow_history_service,
    get_book_borrow_history_service,
)


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


@borrow_router.get("/active", response_model=list[BorrowRecordResponse])
async def get_active_borrows(db: AsyncSession = Depends(get_db)):
    return await get_active_borrows_service(db)


@borrow_router.get("/history", response_model=list[BorrowRecordResponse])
async def get_borrow_history(db: AsyncSession = Depends(get_db)):
    return await get_borrow_history_service(db)


@borrow_router.get("/users/{user_id}/borrow-history", response_model=list[BorrowRecordResponse])
async def get_user_borrow_history(user_id: int, db: AsyncSession = Depends(get_db)):
    return await get_user_borrow_history_service(db, user_id)


@borrow_router.get("/books/{book_id}/borrow-history", response_model=list[BorrowRecordResponse])
async def get_book_borrow_history(book_id: int, db: AsyncSession = Depends(get_db)):
    return await get_book_borrow_history_service(db, book_id)