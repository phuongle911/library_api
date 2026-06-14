from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as http_status

from app.DAO.idempotency_dao import IdempotencyDAO
from app.domain.services.borrow_domain_service import BorrowDomainService
from app.infrastructure.repositories.outbox_repository import OutboxRepository
from app.modules.borrow_service.clients.book_client import BookClient
from app.modules.borrow_service.clients.user_client import UserClient
from app.modules.borrow_service.repository import BorrowRepository


class BorrowApplicationService:

    @staticmethod
    async def borrow_book(
        db: AsyncSession,
        book_id: int,
        user_id: int,
        idempotency_key: str | None = None,
    ):
        try:
            existing_key = None

            if idempotency_key:
                existing_key = await IdempotencyDAO.get(db, idempotency_key)

            if existing_key and existing_key.status == "completed":
                return existing_key.response

            async with db.begin():
                idempotency_record = None

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

                await book_client.reserve_book(book_id=book_id)

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

                await OutboxRepository.create(
                    db=db,
                    event_type="BookBorrowed",
                    payload={
                        "user_id": user_id,
                        "book_id": book_id,
                        "borrowed_at": datetime.now(timezone.utc).isoformat(),
                    },
                )

                if idempotency_record:
                    await IdempotencyDAO.mark_completed(
                        db=db,
                        record=idempotency_record,
                        response=response,
                    )

                return response

        except IntegrityError:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail="Borrow request conflicts with existing data",
            )
