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
    async def get_user_history(
        db: AsyncSession,
        user_id: int,
        record_status: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[BorrowRecord]:
        stmt = select(BorrowRecord).where(BorrowRecord.user_id == user_id)
        if record_status is not None:
            stmt = stmt.where(BorrowRecord.status == record_status)
        stmt = (
            stmt.order_by(BorrowRecord.borrowed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_book_history(
        db: AsyncSession,
        book_id: int,
        record_status: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[BorrowRecord]:
        stmt = select(BorrowRecord).where(BorrowRecord.book_id == book_id)
        if record_status is not None:
            stmt = stmt.where(BorrowRecord.status == record_status)
        stmt = (
            stmt.order_by(BorrowRecord.borrowed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_active_by_user_and_book(
        db: AsyncSession,
        user_id: int,
        book_id: int,
    ) -> BorrowRecord | None:
        result = await db.execute(
            select(BorrowRecord).where(
                BorrowRecord.user_id == user_id,
                BorrowRecord.book_id == book_id,
                BorrowRecord.status == "borrowed",
            )
        )
        return result.scalars().first()


    @staticmethod
    async def get_by_id_for_update(db: AsyncSession, borrow_record_id: int):
        result = await db.execute(
            select(BorrowRecord)
            .where(BorrowRecord.id == borrow_record_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()
