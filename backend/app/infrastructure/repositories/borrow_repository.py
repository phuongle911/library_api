from app.DAO.borrow_records_dao import BorrowRecordsDAO


class BorrowRepository:

    @staticmethod
    async def get_active_by_user_and_book(
        db,
        user_id: int,
        book_id: int,
    ):
        return await BorrowRecordsDAO.get_active_by_user_and_book(
            db=db,
            user_id=user_id,
            book_id=book_id,
        )
    
    @staticmethod
    async def create(
        db,
        user_id: int,
        book_id: int,
    ):
        return await BorrowRecordsDAO.create(
            db=db,
            user_id=user_id,
            book_id=book_id,
        )
        
    @staticmethod
    async def get_by_id_for_update(
        db,
        borrow_record_id: int,
    ):
        return await BorrowRecordsDAO.get_by_id_for_update(
            db=db,
            borrow_record_id=borrow_record_id,
        )
