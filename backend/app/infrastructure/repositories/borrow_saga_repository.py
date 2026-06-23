from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.borrow_saga import BorrowSaga


class BorrowSagaRepository:
    
    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        book_id: int,
        status: str,
    ):
        saga = BorrowSaga(
            user_id=user_id,
            book_id=book_id,
            status=status,
        )

        db.add(saga)
        await db.flush()

        return saga
    
    @staticmethod
    async def update_status(
        db: AsyncSession,
        saga: BorrowSaga,
        status: str,
    ):
        saga.status = status

        await db.flush()

        return saga
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        saga_id: int,
    ):
        result = await db.execute(
            select(BorrowSaga).where(
                BorrowSaga.id == saga_id,
            )
        )

        return result.scaler_one_or_none()
    
    @staticmethod
    async def get_by_status(
        db: AsyncSession,
        status: str,
    ):
        result = await db.execute(
            select(BorrowSaga).where(
                BorrowSaga.status == status,
            )
        )

        return result.scalars().all()
