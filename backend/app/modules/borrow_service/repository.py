from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.borrow_record import BorrowRecord


class BorrowRepository:

    @staticmethod
    async def get_active_by_user_and_book(
        db: AsyncSession,
        user_id: int,
        book_id: int,
    ):
        result = await db.execute(
            select(BorrowRecord).where(
                BorrowRecord.user_id == user_id,
                BorrowRecord.book_id == book_id,
                BorrowRecord.returned_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        book_id: int,
    ):
        borrow_record = BorrowRecord(
            user_id=user_id,
            book_id=book_id,
            borrowed_at=datetime.now(timezone.utc),
            returned_at=None,
        )

        db.add(borrow_record)
        await db.flush()

        return borrow_record

    @staticmethod
    async def get_by_id_for_update(
        db: AsyncSession,
        borrow_record_id: int,
    ):
        result = await db.execute(
            select(BorrowRecord)
            .where(BorrowRecord.id == borrow_record_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active(db: AsyncSession):
        result = await db.execute(
            select(BorrowRecord).where(
                BorrowRecord.returned_at.is_(None),
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_history(db: AsyncSession):
        result = await db.execute(select(BorrowRecord))
        return result.scalars().all()

    @staticmethod
    async def get_user_history(
        db: AsyncSession,
        user_id: int,
        record_status: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ):
        stmt = select(BorrowRecord).where(
            BorrowRecord.user_id == user_id
        )

        if record_status == "borrowed":
            stmt = stmt.where(BorrowRecord.returned_at.is_(None))

        if record_status == "returned":
            stmt = stmt.where(BorrowRecord.returned_at.is_not(None))

        stmt = stmt.offset(offset).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_book_history(
        db: AsyncSession,
        book_id: int,
        record_status: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ):
        stmt = select(BorrowRecord).where(
            BorrowRecord.book_id == book_id
        )

        if record_status == "borrowed":
            stmt = stmt.where(BorrowRecord.returned_at.is_(None))

        if record_status == "returned":
            stmt = stmt.where(BorrowRecord.returned_at.is_not(None))

        stmt = stmt.offset(offset).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()
