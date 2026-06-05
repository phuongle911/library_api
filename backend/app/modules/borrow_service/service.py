from fastapi import HTTPException
from starlette import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from app.modules.borrow_service.repository import BorrowRepository
from app.modules.borrow_service.clients.user_client import UserClient
from app.modules.borrow_service.clients.book_client import BookClient
from app.domain.services.return_domain_service import ReturnDomainService
from app.domain.services.borrow_domain_service import BorrowDomainService
from app.domain.events.dispatcher import dispatch_domain_event
from app.domain.events.book_borrowed import BookBorrowed
from app.domain.events.book_returned import BookReturned
from app.DAO.idempotency_dao import IdempotencyDAO
from app.models.outbox_event import OutboxEvent
from app.infrastructure.repositories.outbox_repository import OutboxRepository


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

            book_client = BookClient()
            user_client = UserClient()

            book = await book_client.get_book_for_update(
                db=db,
                book_id=book_id,
            )

            if not await user_client.get_user(db, user_id):
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="User not found",
                )


            if not book:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Book not found",
                )

            active_borrow = await BorrowRepository.get_active_by_user_and_book(
                db=db,
                user_id=user_id,
                book_id=book_id,
            )
            try:
                BorrowDomainService.validate_can_borrow(
                    active_borrow=active_borrow,
                    book=book,
                )

            except ValueError as e:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=str(e),
                )

            book.available_copies -= 1

            borrow_record = await BorrowRepository.create(
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

        await OutboxRepository.create(
            db=db,
            event_type="BookBorrowed",
            payload={
                "user_id": user_id,
                "book_id": book_id,
                "borrowed_at": datetime.now(timezone.utc).isoformat(),
            },
        )


        return response

    except IntegrityError:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Borrow request conflicts with existing data",
        )


async def check_book_availability_service(
        db: AsyncSession,
        book_id: int,
            ):
    book_client = BookClient()
    
    book = await book_client.get_book(
        db=db,
        book_id=book_id,
    )

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


async def get_active_borrows_service(db: AsyncSession):
    return await BorrowRepository.get_active(db)


async def get_borrow_history_service(db: AsyncSession):
    return await BorrowRepository.get_history(db)


async def get_user_borrow_history_service(
    db: AsyncSession,
    user_id: int,
    status: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    return await BorrowRepository.get_user_history(
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
    return await BorrowRepository.get_book_history(
        db,
        book_id,
        record_status=status,
        limit=limit,
        offset=offset,
    )


async def return_book_service(
        db: AsyncSession,
        borrow_record_id: int,
):
    async with db.begin():
        borrow_record = await BorrowRepository.get_by_id_for_update(
            db=db,
            borrow_record_id=borrow_record_id,
        )

        try:
            ReturnDomainService.validate_can_ruturn(borrow_record)

        except ValueError as e:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        
        user_client = UserClient()
        book_client = BookClient()

        book = await book_client.get_book_for_update(
            db=db,
            book_id=borrow_record.book_id,
        )
        
        if not book:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Book not found",
            )
        
        borrow_record.returned_at = datetime.now(timezone.utc)
        book.available_copies += 1

        response = {
            "borrow_record_id": str(borrow_record.id),
            "book_id": str(borrow_record.book_id),
            "user_id": str(borrow_record.user_id),
            "status": "returned",
        }

        event = BookReturned(
            user_id=borrow_record.user_id,
            book_id=borrow_record.book_id,
            borrow_record_id=borrow_record.id,
            returned_at=borrow_record.returned_at,
        )

        await dispatch_domain_event(event)
        return response
    

async def check_book_availability_service(
        db: AsyncSession,
        book_id: int,
            ):
    book_client = BookClient()

    book = await book_client.get_book(db, book_id)

    if not book:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    return {
        "book_id": book.id,
        "title": book.title,
        "is_available": book.is_available,
        "available_copies": book.available_copies,
    }
