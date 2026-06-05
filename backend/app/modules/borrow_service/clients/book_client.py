import os
import httpx

from app.infrastructure.repositories.book_repository import BookRepository
from app.modules.borrow_service.contracts.book_contract import BookContract

INTERNAL_API_BASE_URL = os.getenv(
    "INTERNAL_API_BASE_URL",
    "http://backend:8000/api/v1",
)

INTERNAL_API_TOKEN = os.getenv(
    "INTERNAL_API_TOKEN",
    "dev-internal-token",
)


class BookClient:
    async def get_book_for_update(self, db, book_id: int):
        """
        Future:
        GET /books/{id}
        """
        return await BookRepository.get_by_id(db, book_id)

    async def get_book(self, db, book_id: int) -> BookContract | None:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{INTERNAL_API_BASE_URL}/internal/books/{book_id}",
                headers={"X-Internal-Token": INTERNAL_API_TOKEN},
            )

            if response.status_code == 404:
                return None
            
            response.raise_for_status()

            data = response.json()

            return BookContract(
                id=data["id"],
                title=data["title"],
                available_copies=data["available_copies"],
            )
