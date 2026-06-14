from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from starlette import status as http_status
from datetime import datetime, timezone

from app.infrastructure.repositories.borrow_repository import BorrowRepository
from app.domain.services.return_domain_service import ReturnDomainService
from app.modules.borrow_service.clients.book_client import BookClient
from app.domain.events.book_returned import BookReturned
from app.domain.events.dispatcher import dispatch_domain_event


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
        
        book_client = BookClient()

        book = await book_client.get_book(
            db=db,
            book_id=borrow_record.book_id,
        )

        if not book:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Book not found",
            )
        
        borrow_record.returned_at = datetime.now(timezone.utc)

        await book_client.release_book(
            book_id=borrow_record.book_id,
        )
    
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
