from app.modules.book_service.repository import BooksDAO


class BookClient:
    async def get_book_for_update(self, db, book_id: int):
        return await BooksDAO.get_by_id_for_update(db, book_id)