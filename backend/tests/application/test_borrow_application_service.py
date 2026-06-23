import pytest
from datetime import datetime, timezone

from app.application.borrow_application_service import BorrowApplicationService


class FakeUserClient:
    async def get_user(self, db, user_id: int):
        return {
            "id": user_id,
            "name": "Test User",
        }


class FakeBookGrpcClient:
    async def get_book(self, book_id: int):
        class Book:
            id = book_id
            title = "Clean Code"
            available_copies = 2

        return Book()

    async def reserve_book(self, book_id: int):
        class Reservation:
            success = True
            message = "Book reserved successfully"

        return Reservation()

    async def confirm_reservation(self, book_id: int):
        class Response:
            success = True
            message = "Reservation confirmed"

        return Response()
    
    async def cancel_reservation(self, book_id: int):
        class Response:
            success = True
            message = "Reservation cancelled"

        return Response()


class FakeBorrowRecord:
    id = 1
    status = "borrowed"
    borrowed_at = datetime.now(timezone.utc)
    returned_at = None


class FakeBorrowRepository:
    @staticmethod
    async def get_active_by_user_and_book(db, user_id: int, book_id: int):
        return None

    @staticmethod
    async def create(db, user_id: int, book_id: int):
        return FakeBorrowRecord()


class FakeOutboxRepository:
    @staticmethod
    async def create(db, event_type: str, payload: dict):
        return None


@pytest.mark.asyncio
async def test_borrow_book_success(monkeypatch, async_session):
    monkeypatch.setattr(
        "app.application.borrow_application_service.BookGrpcClient",
        FakeBookGrpcClient,
    )

    monkeypatch.setattr(
        "app.application.borrow_application_service.UserClient",
        FakeUserClient,
    )

    monkeypatch.setattr(
        "app.application.borrow_application_service.BorrowRepository",
        FakeBorrowRepository,
    )

    monkeypatch.setattr(
        "app.application.borrow_application_service.OutboxRepository",
        FakeOutboxRepository,
    )

    result = await BorrowApplicationService.borrow_book(
        db=async_session,
        book_id=1,
        user_id=1,
    )

    assert result["status"] == "borrowed"
    assert result["book_id"] == "1"
    assert result["user_id"] == "1"
