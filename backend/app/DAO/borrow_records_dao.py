from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 

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
    

    @staticmethod
    async def get_active(db: AsyncSession) -> list[BorrowRecord]:
        result = await db.execute(
            select(BorrowRecord)
            .order_by(BorrowRecord.borrowed_at.desc())
        )
        return list(result.scalars().all())
    

    @staticmethod
    async def get_history(db: AsyncSession) -> list[BorrowRecord]:
        result = await db.execute(
            select(BorrowRecord)
            .order_by(BorrowRecord.borrowed_at.desc())
        )
        return list(result.scalars().all())
    

    @staticmethod
    async def get_user_history(db: AsyncSession, user_id: int) -> list[BorrowRecord]:
        result = await db.execute(
            select(BorrowRecord)
            .where(BorrowRecord.user_id == user_id)
            .order_by(BorrowRecord.borrowed_at.desc())
        )
        return list(result.scalars().all())
    

    @staticmethod
    async def get_book_history(db: AsyncSession, book_id: int) -> list[BorrowRecord]:
        result = await db.execute(
            select(BorrowRecord)
            .where(BorrowRecord.book_id == book_id)
            .order_by(BorrowRecord.borrowed_at.desc())
        )
        return list(result.scalars().all())