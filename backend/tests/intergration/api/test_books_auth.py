import pytest
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.books import Book
from app.models.categories import Category
from backend.app.modules.book_service.books import BookUpdate
from backend.app.modules.book_service.book_service import (
    update_book_service,
    delete_book_service,
)


@pytest.mark.asyncio
async def test_update_book_other_user_forbidden(async_session: AsyncSession):
    owner = User(
        email=f"owner-{uuid.uuid4()}@test.com",
        hashed_password="x",
        role="user"
        )
    other = User(
        email=f"other-{uuid.uuid4()}@test.com",
        hashed_password="x",
        role="user"
        )

    category = Category(name=f"Fiction-{uuid.uuid4()}")
    async_session.add_all([owner, other, category])
    await async_session.commit()
    await async_session.refresh(owner)
    await async_session.refresh(other)
    await async_session.refresh(category)

    book = Book(title="old", author="a", owner_id=owner.id, category_id=category.id)

    async_session.add(book)
    await async_session.commit()
    await async_session.refresh(book)

    payload = BookUpdate(title="fail")

    with pytest.raises(HTTPException) as exc:
        await update_book_service(async_session, book.id, payload, other)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_update_book_admin_success(async_session: AsyncSession):
    owner = User(
        email=f"owner-{uuid.uuid4()}@test.com",
        hashed_password="x",
        role="user"
        )
    admin = User(
        email=f"admin-{uuid.uuid4()}@test.com",
        hashed_password="x",
        role="admin"
        )

    category = Category(name=f"Fiction-{uuid.uuid4()}")
    async_session.add_all([owner, admin, category])
    await async_session.commit()
    await async_session.refresh(owner)
    await async_session.refresh(admin)
    await async_session.refresh(category)

    book = Book(title="old", author="a", owner_id=owner.id, category_id=category.id)
    async_session.add(book)
    await async_session.commit()
    await async_session.refresh(book)

    payload = BookUpdate(title="admin-update")

    updated = await update_book_service(async_session, book.id, payload, admin)

    assert updated.title == "admin-update"


@pytest.mark.asyncio
async def test_update_book_owner_success(async_session: AsyncSession):
    owner = User(
        email=f"owner-{uuid.uuid4()}@test.com",
        hashed_password="x",
        role="user"
        )

    category = Category(name=f"Fiction-{uuid.uuid4()}")
    async_session.add_all([owner, category])
    await async_session.commit()
    await async_session.refresh(owner)
    await async_session.refresh(category)

    book = Book(title="old", author="a", owner_id=owner.id, category_id=category.id)
    async_session.add(book)
    await async_session.commit()
    await async_session.refresh(book)

    payload = BookUpdate(title="new")

    updated = await update_book_service(async_session, book.id, payload, owner)

    assert updated.title == "new"


@pytest.mark.asyncio
async def test_delete_book_owner_success(async_session: AsyncSession):
    owner = User(
        email=f"owner-{uuid.uuid4()}@test.com",
        hashed_password="x",
        role="user"
        )

    category = Category(name=f"Fiction-{uuid.uuid4()}")
    async_session.add_all([owner, category])
    await async_session.commit()
    await async_session.refresh(owner)
    await async_session.refresh(category)

    book = Book(title="t", author="a", owner_id=owner.id, category_id=category.id)
    async_session.add(book)
    await async_session.commit()
    await delete_book_service(async_session, book.id, owner)

    delete = await async_session.get(Book, book.id)
    assert delete is None


@pytest.mark.asyncio
async def test_delete_book_admin_success(async_session: AsyncSession):
    owner = User(
        email=f"owner-{uuid.uuid4()}@test.com",
        hashed_password="x",
        role="user"
        )
    admin = User(
        email=f"admin-{uuid.uuid4()}@test.com",
        hashed_password="x",
        role="admin"
        )

    category = Category(name=f"Fiction-{uuid.uuid4()}")
    async_session.add_all([owner, admin, category])
    await async_session.commit()
    await async_session.refresh(owner)
    await async_session.refresh(admin)
    await async_session.refresh(category)

    book = Book(title="t", author="a", owner_id=owner.id, category_id=category.id)
    async_session.add(book)
    await async_session.commit()

    await delete_book_service(async_session, book.id, admin)

    deleted = await async_session.get(Book, book.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_book_other_user_forbidden(async_session: AsyncSession):
    owner = User(
        email=f"owner-{uuid.uuid4()}@test.com",
        hashed_password="x",
        role="user"
        )
    other = User(
        email=f"other-{uuid.uuid4()}@test.com",
        hashed_password="x",
        role="user"
        )

    category = Category(name=f"Fiction-{uuid.uuid4()}")
    async_session.add_all([owner, other, category])
    await async_session.commit()
    await async_session.refresh(owner)
    await async_session.refresh(other)
    await async_session.refresh(category)

    book = Book(title="t", author="a", owner_id=owner.id, category_id=category.id)
    async_session.add(book)
    await async_session.commit()

    with pytest.raises(HTTPException) as exc:
        await delete_book_service(async_session, book.id, other)

        assert exc.value.status_code == 403
