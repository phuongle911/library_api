from app.DAO.books_dao import BooksDAO


class  BookRepository:

    @staticmethod
    async def get_by_id_for_update(db, book_id: int):
        return await BooksDAO.get_by_id_for_update(db, book_id)
