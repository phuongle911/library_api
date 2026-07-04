from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.borrow_history_read_model import BorrowHistoryReadModel


class BorrowHistoryReadRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        borrow_record_id: int,
        user_id: int,
        book_id: int,
        book_title: str,
        borrow_status: str,
        borrowed_at,
        returned_at=None,
    ):
        read_model = BorrowHistoryReadModel(
            borrow_record_id=borrow_record_id,
            user_id=user_id,
            book_id=book_id,
            book_title=book_title,
            borrow_status=borrow_status,
            borrowed_at=borrowed_at,
            returned_at=returned_at,
        )

        db.add(read_model)
        await db.flush()

        return read_model
    
    @staticmethod
    async def get_by_user_id(
        db: AsyncSession,
        user_id: int
    ):
        result = await db.execute(
            select(BorrowHistoryReadModel)
            .where(BorrowHistoryReadModel.user_id == user_id)
        )

        return result.scalars().all()

    @staticmethod
    async def get_by_borrow_record_id(
        db: AsyncSession,
        borrow_record_id: int,
    ):
        result = await db.execute(
            select(BorrowHistoryReadModel)
            .where(BorrowHistoryReadModel.borrow_record_id == borrow_record_id)
        )
    
        return result.scalar_one_or_none()

    @staticmethod
    async def update_status(
        db: AsyncSession,
        read_model: BorrowHistoryReadModel,
        status: str,
        returned_at=None,
    ):
        read_model.borrow_status = status
        read_model.returned_at = returned_at

        await db.flush()

        return read_model
