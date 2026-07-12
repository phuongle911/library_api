from sqlalchemy.ext.asyncio import AsyncSession

from app.application.borrow_application_service import BorrowApplicationService


class BorrowBookUseCase:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(
            self,
            book_id: int,
            user_id: int,
            idempotency_key: str | None = None,
            ):
        return await BorrowApplicationService.borrow_book(
            db=self.db,
            book_id=book_id,
            user_id=user_id,
            idempotency_key=idempotency_key,
        )
