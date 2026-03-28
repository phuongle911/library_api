import pytest
from types import SimpleNamespace
from fastapi import HTTPException
from unittest.mock import AsyncMock, Mock

from app.DAO.books_dao import BooksDAO
from app.schemas.books import BookCreate, BookUpdate
from app.services.book_service import (
    create_book_service,
    get_book_service,
    list_books_service,
    update_book_service,
    delete_book_service,
)
from tests.conftest import set_execute_first


def mock_db_title_exists(db, exists: bool):
    result = Mock()
    scalars = Mock()
    scalars.first.return_value = object() if exists else None
    result.scalars.return_value = scalars
    db.execute.return_value = result


def make_user(user_id=1):
    return SimpleNamespace(id=user_id)

def make_book(book_id=1, owner_id=1, **kwargs):
    base = {
        "id": book_id,
        "owner_id": owner_id,
        "title": "T",
        "author": "A",
        "description": "D"
    }
    base.update(kwargs)
    return SimpleNamespace(**base)

@pytest.fixture
def db():
    db = Mock()
    db.add = Mock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    db.execute = AsyncMock()
    db.get = AsyncMock()
    return db

@pytest.fixture
def user():
    return make_user(1)

@pytest.fixture
def other_user():
    return make_user(2)

@pytest.fixture
def mock_cache(mocker):
    return {
        "get": mocker.patch("app.services.book_service.get_books_list_cache", return_value=None),
        "set": mocker.patch("app.services.book_service.set_books_list_cache"),
        "invalidate": mocker.patch("app.services.book_service.invalidate_books_list_cache"),
    }

@pytest.fixture
def mock_dao(mocker):
    return mocker.patch(
        "app.services.book_service.BooksDAO.list_by_owner_paginated",
        new=AsyncMock(return_value=([],0)),
    )


@pytest.mark.asyncio
async def test_create_book_title_exists(db, user, mocker):
    mocker.patch(
        "app.services.book_service.BooksDAO.get_by_title",
        new=Mock(return_value=make_book()),
    )

    mocker.patch(
        "app.services.book_service.CategoriesDAO.get_by_id",
        new=AsyncMock(return_value=object()),
    )

    payload = BookCreate(
        title="Clean Code",
        author="Robert",
        description="XO",
        category_id=123,
    )

    with pytest.raises(HTTPException) as e:
        await create_book_service(db, payload, user)

    assert e.value.status_code == 400


@pytest.mark.asyncio
async def test_create_book_success(db, user, mock_cache, mocker):
    mocker.patch(
        "app.services.book_service.CategoriesDAO.get_by_id",
        new=AsyncMock(return_value=object()),
    )
    mocker.patch(
        "app.services.book_service.BooksDAO.get_by_title",
        new=Mock(return_value=None),
    )

    payload = BookCreate(
        title="Clean Code Continue",
        author="Robert",
        description="XO",
        category_id=123,
    )

    book = await create_book_service(db, payload, user)

    db.add.assert_called_once()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()
    assert book.owner_id == user.id


@pytest.mark.asyncio
async def test_get_book_404(db):
    db.get = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as e:
        await get_book_service(123, db)

    assert e.value.status_code == 404


@pytest.mark.asyncio
async def test_get_book_success(db):
    book = make_book(book_id=5)
    db.get = AsyncMock(return_value=book)

    got = await get_book_service(5, db)
    assert got == book


@pytest.mark.asyncio
async def test_list_books_cache_hit(db, user, mocker, mock_dao):
    cached = {"items": ["X"], "meta": {"page": 1}}

    mocker.patch("app.services.book_service.get_books_list_cache", return_value=cached)

    result = await list_books_service(db, user, page=1, page_size=10)
    assert result == cached
    mock_dao.assert_not_called()


@pytest.mark.asyncio
async def test_list_books_calls_dao_and_sets_cache(db, user, mock_cache, mocker):
    dao = mocker.patch(
        "app.services.book_service.BooksDAO.list_by_owner_paginated",
        new=AsyncMock(return_value=(["b1","b2"], 25)),
    )

    result = await list_books_service(db, user, page=1, page_size=10, sort_dir="DESC")

    assert result["items"] == ["b1","b2"]
    assert result["meta"]["total_pages"] == 3

    called_kwargs = dao.await_args.kwargs
    assert called_kwargs["owner_id"] == user

    mock_cache["set"].assert_called_once()


@pytest.mark.asyncio
async def test_update_book_404(db, user):
    db.get = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as e:
        await update_book_service(db, 1, BookUpdate(title="XO", author="Ann", description="anyhting"), user)

    assert e.value.status_code == 404


@pytest.mark.asyncio
async def test_update_book_403(db, user):
    db.get = AsyncMock(return_value=make_book(owner_id=999))

    with pytest.raises(HTTPException) as e:
        await update_book_service(db, 1, BookUpdate(title="XO", author="Ann", description="anything"), user)

    assert e.value.status_code == 403


@pytest.mark.asyncio
async def test_update_book_success(db, user, mock_cache):
    book = make_book(owner_id=user.id, title="Old")
    db.get = AsyncMock(return_value=book)

    updated = await update_book_service(db, 1, BookUpdate(title="New", author="Ann", description="anything"), user)

    assert updated.title == "New"
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()

    mock_cache["invalidate"].assert_called_once_with(user_id=user.id)


@pytest.mark.asyncio
async def test_delete_book_404(db, user):
    db.get = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as e:
        await delete_book_service(db, 1, user)

    assert e.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_book_403(db, user):
    db.get = AsyncMock(return_value=make_book(owner_id=999))

    with pytest.raises(HTTPException) as e:
        await delete_book_service(db, 1, user)

    assert e.value.status_code == 403


@pytest.mark.asyncio
async def test_delete_book_success(db, user, mock_cache):
    book = make_book(owner_id=user.id)
    db.get = AsyncMock(return_value=book)

    result = await delete_book_service(db, 1, user)

    db.delete.assert_awaited_once_with(book)
    db.commit.assert_awaited_once()

    mock_cache["invalidate"].assert_called_once_with(user_id=user.id)
    assert result == {"message": "Book deleted"}