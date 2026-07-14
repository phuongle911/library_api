import httpx
import pytest
from fastapi import HTTPException

from app.modules.borrow_service.clients.book_client import BookClient


@pytest.mark.asyncio
async def test_get_book_success(mocker):
    client = BookClient()

    mock_response = httpx.Response(
        status_code=200,
        json={
            "id": 1,
            "title": "Clean Code",
            "available_copies": 3,
        },
        request=httpx.Request(
            method="GET",
            url="http://test/internal/books/1",
        ),
    )

    mocker.patch.object(
        client,
        "_fetch_book_from_internal_api",
        return_value=mock_response,
    )

    book = await client.get_book(db=None, book_id=1)

    assert book.id == 1
    assert book.title == "Clean Code"
    assert book.available_copies == 3
    assert book.is_available is True


@pytest.mark.asyncio
async def test_get_book_not_found(mocker):
    client = BookClient()

    mock_response = httpx.Response(
        status_code=404,
        request=httpx.Request(
            method="GET",
            url="http://test/internal/books/999",
        ),
    )

    mocker.patch.object(
        client,
        "_fetch_book_from_internal_api",
        return_value=mock_response,
    )

    book = await client.get_book(db=None, book_id=999)

    assert book is None


@pytest.mark.asyncio
async def test_get_book_service_unavailable(mocker):
    client = BookClient()

    mocker.patch.object(
        client,
        "_fetch_book_from_internal_api",
        side_effect=httpx.RequestError("Service down"),
    )

    with pytest.raises(HTTPException) as exc:
        await client.get_book(db=None, book_id=1)

    assert exc.value.status_code == 503
    assert exc.value.detail == "Book service unavailable"


@pytest.mark.asyncio
async def test_get_book_timeout(mocker):
    client = BookClient()

    mocker.patch.object(
        client,
        "_fetch_book_from_internal_api",
        side_effect=httpx.TimeoutException("Timeout"),
    )

    with pytest.raises(HTTPException) as exc:
        await client.get_book(db=None, book_id=1)

    assert exc.value.status_code == 504
    assert exc.value.detail == "Book service timeout"
