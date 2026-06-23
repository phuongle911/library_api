from app.infrastructure.repositories.borrow_history_read_repository import BorrowHistoryReadRepository


class GetBorrowHistoryService:

    @staticmethod
    async def execute(db, user_id: int):
        return await BorrowHistoryReadRepository.get_by_user_id(
            db=db,
            user_id=user_id,
        )
