from app.application.cache import get_cache, set_cache
from app.infrastructure.repositories.borrow_history_read_repository import (
    BorrowHistoryReadRepository,
)


class GetBorrowHistoryService:

    @staticmethod
    async def execute(db, user_id: int):
        cache_key = f"borrow_history:user:{user_id}"

        cached_data = await get_cache(cache_key)

        if cached_data:
            return cached_data

        records = await BorrowHistoryReadRepository.get_by_user_id(
            db=db,
            user_id=user_id,
        )

        response = [
            {
                "borrow_record_id": record.borrow_record_id,
                "user_id": record.user_id,
                "book_id": record.book_id,
                "book_title": record.book_title,
                "borrow_status": record.borrow_status,
                "borrowed_at": record.borrowed_at,
                "returned_at": record.returned_at,
            }
            for record in records
        ]

        await set_cache(
            key=cache_key,
            value=response,
            ttl_seconds=60,
        )

        return response
