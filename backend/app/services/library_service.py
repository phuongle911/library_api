import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.DAO.books_dao import BooksDAO
from app.schemas.books import BookCreate


logger = logging.getLogger(__name__)


class LibraryService:
    def __init__(self) -> None:
        self.books = BooksDAO()

    async def create_book_with_log(
            self,
            db: AsyncSession,
            data: BookCreate,
            owner_id: int,
    ):
        book = await self.books.create(db, data, owner_id)
        # logger.info("book_created owner_id=%s book_id=%s", owner_id, book.id)
        return book
