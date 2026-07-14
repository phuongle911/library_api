from fastapi import APIRouter, Depends, Query, Header
from typing import Literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_read_db
from app.modules.borrow_service.service import check_book_availability_service
from app.modules.borrow_service.schemas import BorrowBookRequest, BorrowRecordResponse
from app.modules.borrow_service.service import (
    return_book_service,
    get_active_borrows_service,
    get_borrow_history_service,
    get_user_borrow_history_service,
    get_book_borrow_history_service,
)
from app.application.use_cases.borrow_book import BorrowBookUseCase
from app.application.borrow_application_service import BorrowApplicationService
from app.application.get_borrow_history_service import GetBorrowHistoryService

borrow_router = APIRouter(prefix="/borrow", tags=["Borrow"])


@borrow_router.post("/books/{book_id}")
async def borrow_book(
    book_id: int,
    payload: BorrowBookRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
):
    print(f"Text: {payload}")
    use_case = BorrowBookUseCase(db)
    return await use_case.execute(
        book_id=book_id,
        user_id=payload.user_id,
        idempotency_key=idempotency_key,
    )


@borrow_router.get("/active", response_model=list[BorrowRecordResponse])
async def get_active_borrows(db: AsyncSession = Depends(get_read_db)):
    return await get_active_borrows_service(db)


@borrow_router.get("/history", response_model=list[BorrowRecordResponse])
async def get_list_borrow_history(
    status: Literal["borrowed_at", "returned_at"] | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_read_db),
      ):
    return await get_borrow_history_service(
        db=db,
        # status=status,
        # limit=limit,
        # offset=offset,
        )


@borrow_router.get(
        "/users/{user_id}/borrow-history",
        response_model=list[BorrowRecordResponse]
        )
async def get_user_borrow_history(
    user_id: int,
    status: Literal["borrowed", "returned"] | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_read_db),
      ):
    return await get_user_borrow_history_service(
        db=db,
        user_id=user_id,
        status=status,
        limit=limit,
        offset=offset,
    )


@borrow_router.get(
        "/books/{book_id}/borrow-history",
        response_model=list[BorrowRecordResponse]
        )
async def get_book_borrow_history(
    book_id: int,
    status: Literal["borrowed", "returned"] | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_read_db),
      ):
    return await get_book_borrow_history_service(
        db=db,
        book_id=book_id,
        status=status,
        limit=limit,
        offset=offset,
    )


@borrow_router.post("/records/{borrow_record_id}/return")
async def return_book(
    borrow_record_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await return_book_service(
        db=db,
        borrow_record_id=borrow_record_id,
    )


@borrow_router.get("/books/{book_id}/availability")
async def check_book_availability(
    book_id: int,
    db: AsyncSession = Depends(get_read_db),
):
    return await check_book_availability_service(db=db, book_id=book_id)


@borrow_router.get("/users/{user_id}/borrow-history")
async def get_borrow_history(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await GetBorrowHistoryService.execute(
        db=db,
        user_id=user_id,
    )
