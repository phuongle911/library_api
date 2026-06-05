from app.infrastructure.repositories.book_repository import BookRepository
from app.modules.borrow_service.contracts.book_contract import BookContract


class BookClient:
    async def get_book_for_update(self, db, book_id: int):
        """
        Future:
        GET /books/{id}
        """
        return await BookRepository.get_by_id(db, book_id)

    async def get_book(self, db, book_id: int) -> BookContract | None:
        book = await BookRepository.get_by_id(db, book_id)

        if not book:
            return None
        
        return BookContract(
            id=book.id,
            title=book.title,
            available_copies=book.available_copies,
        )
