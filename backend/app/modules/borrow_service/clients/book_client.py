from app.modules.book_service.repository import BooksDAO
from app.infrastructure.repositories.book_repository import BookRepository


class BookClient:
    async def get_book_for_update(self, db, book_id: int):
        """
        Future:
        GET /books/{id}
        """
        return await BookRepository.get_by_id_for_update(db, book_id)
