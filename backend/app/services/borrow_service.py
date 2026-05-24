from fastapi import HTTPException
from starlette import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.domain.events.dispatcher import dispatch_domain_event
from app.domain.events.book_borrowed import BookBorrowed
from app.DAO.users_dao import UsersDAO
from app.DAO.books_dao import BooksDAO
from app.DAO.borrow_records_dao import BorrowRecordsDAO
from app.DAO.idempotency_dao import IdempotencyDAO


async def borrow_book_service(
    db: AsyncSession,
    book_id: int,
    user_id: int,
    idempotency_key: str | None = None,
):
    try:
        # 1. Check if this request was already completed
        if idempotency_key:
            existing_key = await IdempotencyDAO.get(db, idempotency_key)

            if existing_key and existing_key.status == "completed":
                return existing_key.response

        async with db.begin():
            idempotency_record = None

            # 2. Save key as processing
            if idempotency_key:
                idempotency_record = await IdempotencyDAO.create_processing(
                    db=db,
                    key=idempotency_key,
                )

            user = await UsersDAO.get_by_id(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="User not found",
                )

            book = await BooksDAO.get_by_id_for_update(db, book_id)
            if not book:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Book not found",
                )

            active_borrow = await BorrowRecordsDAO.get_active_by_user_and_book(
                db=db,
                user_id=user_id,
                book_id=book_id,
            )
            if active_borrow:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="User already has this book borrowed",
                )

            if book.available_copies <= 0:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="No available copies left",
                )

            book.available_copies -= 1

            borrow_record = await BorrowRecordsDAO.create(
                db=db,
                user_id=user_id,
                book_id=book_id,
            )

            response = {
                "borrow_record_id": str(borrow_record.id),
                "book_id": str(book_id),
                "user_id": str(user_id),
                "status": "borrowed",
            }

            # 3. Save final response against idempotency key
            if idempotency_record:
                await IdempotencyDAO.mark_completed(
                    db=db,
                    record=idempotency_record,
                    response=response,
                )

        event = BookBorrowed(
            user_id=user_id,
            book_id=book_id,
            borrowed_at=datetime.now(timezone.utc),
        )

        await dispatch_domain_event(event)
        return response

    except IntegrityError:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Borrow request conflicts with existing data",
        )


async def get_active_borrows_service(db: AsyncSession):
    return await BorrowRecordsDAO.get_active(db)


async def get_borrow_history_service(db: AsyncSession):
    return await BorrowRecordsDAO.get_history(db)


async def get_user_borrow_history_service(
    db: AsyncSession,
    user_id: int,
    status: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    return await BorrowRecordsDAO.get_user_history(
        db,
        user_id,
        record_status=status,
        limit=limit,
        offset=offset,
    )


async def get_book_borrow_history_service(
    db: AsyncSession,
    book_id: int,
    status: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    return await BorrowRecordsDAO.get_book_history(
        db,
        book_id,
        record_status=status,
        limit=limit,
        offset=offset,
    )
