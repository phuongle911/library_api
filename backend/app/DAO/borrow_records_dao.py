from sqlalchemy.ext.asyncio import AsyncSession

from app.models.borrow_record import BorrowRecord


class BorrowRecordsDAO:
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        book_id: int   
         ) -> BorrowRecord:
        record = BorrowRecord(
            user_id=user_id,
            book_id=book_id,
            status="borrowed",
        )
        db.add(record)
        await db.flush()
        return record