import os
import httpx

from fastapi import HTTPException
from starlette import status as http_status
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
)

from app.infrastructure.repositories.book_repository import BookRepository
from app.modules.borrow_service.contracts.book_contract import BookContract
from app.internal.circuit_breaker import CircuitBreaker


INTERNAL_API_BASE_URL = os.getenv(
    "INTERNAL_API_BASE_URL",
    "http://backend:8000/api/v1",
)

INTERNAL_API_TOKEN = os.getenv(
    "INTERNAL_API_TOKEN",
    "dev-internal-token",
)

book_service_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=10,
)

class BookClient:

    async def get_book_for_update(self, db, book_id: int):
        """
        Future:
        GET /internal/books/{id}
        """
        return await BookRepository.get_by_id(db, book_id)

    async def get_book(self, db, book_id: int) -> BookContract | None:
        if book_service_circuit_breaker.is_open():
            raise HTTPException(
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Book service circuit is open",
            )

        try:
            response = await self._fetch_book_from_internal_api(book_id)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            book_service_circuit_breaker.record_success()

        except httpx.TimeoutException:
            book_service_circuit_breaker.record_failure()
            raise HTTPException(
                status_code=http_status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Book service timeout",
            )

        except httpx.RequestError:
            book_service_circuit_breaker.record_failure()
            raise HTTPException(
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Book service unavailable",
            )

        data = response.json()

        return BookContract(
            id=data["id"],
            title=data["title"],
            available_copies=data["available_copies"],
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(
            (
                httpx.RequestError,
                httpx.TimeoutException,
            )
        ),
        reraise=True,
    )
    async def _fetch_book_from_internal_api(
        self,
        book_id: int,
    ):
        async with httpx.AsyncClient(timeout=5.0) as client:
            return await client.get(
                f"{INTERNAL_API_BASE_URL}/internal/books/{book_id}",
                headers={
                    "X-Internal-Token": INTERNAL_API_TOKEN,
                },
            )
