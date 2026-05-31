import uuid

import pytest

from app.modules.book_service.repository import BooksDAO
from app.models.books import Book
from app.models.categories import Category
from app.modules.book_service.schemas import BookUpdate


@pytest.mark.asyncio
async def test_create_and_get_by_id(async_session, owner_user):
    category = Category(name=f"test-category-{uuid.uuid4()}")
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    book = Book(
        title="Test Book",
        author="Test Author",
        description="anything",
        owner_id=owner_user.id,
        category_id=category.id,
    )

    created = await BooksDAO.create(async_session, book)
    fetched = await BooksDAO.get_by_id(async_session, created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Test Book"
    assert fetched.owner_id == owner_user.id
    assert fetched.category_id == category.id


@pytest.mark.asyncio
async def test_get_by_title(async_session, owner_user):
    category = Category(name=f"test-category-{uuid.uuid4()}")
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    book = Book(
        title="Unique Title",
        author="Author",
        description="anything",
        owner_id=owner_user.id,
        category_id=category.id,
    )
    await BooksDAO.create(async_session, book)

    fetched = await BooksDAO.get_by_title(async_session, "Unique Title")

    assert fetched is not None
    assert fetched.title == "Unique Title"
    assert fetched.owner_id == owner_user.id


@pytest.mark.asyncio
async def test_list_by_owner_filters_and_sort(async_session, owner_user):
    category = Category(name=f"test-category-{uuid.uuid4()}")
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    await BooksDAO.create(
        async_session,
        Book(
            title="Python Basics",
            author="Alice",
            description="anything",
            owner_id=owner_user.id,
            category_id=category.id,
        ),
    )
    await BooksDAO.create(
        async_session,
        Book(
            title="FastAPI Guide",
            author="Bob",
            description="anything",
            owner_id=owner_user.id,
            category_id=category.id,
        ),
    )
    await BooksDAO.create(
        async_session,
        Book(
            title="Python Advanced",
            author="Charlie",
            description="anything",
            owner_id=owner_user.id,
            category_id=category.id,
        ),
    )

    result = await BooksDAO.list_by_owner(
        async_session,
        owner_id=owner_user.id,
        title="Python",
        sort_by="title",
    )

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].title == "Python Advanced"
    assert result[1].title == "Python Basics"


@pytest.mark.asyncio
async def test_list_by_owner_paginated(async_session, owner_user):
    category = Category(name=f"test-category-{uuid.uuid4()}")
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    owner_id = owner_user.id

    for i in range(1, 26):
        book = Book(
            title=f"Book {i:02d}",
            author="Author",
            description="anything",
            owner_id=owner_id,
            category_id=category.id,
        )
        await BooksDAO.create(async_session, book)

    result = await BooksDAO.list_by_owner(
        async_session,
        owner_id=owner_id,
    )

    assert isinstance(result, list)
    assert len(result) == 25
    assert all(book.owner_id == owner_id for book in result)


@pytest.mark.asyncio
async def test_update(async_session, owner_user):
    category = Category(name=f"test-category-{uuid.uuid4()}")
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    book = Book(
        title="Old Title",
        author="Old Author",
        description="anything",
        owner_id=owner_user.id,
        category_id=category.id,
    )
    book = await BooksDAO.create(async_session, book)

    updated = await BooksDAO.update(
        async_session,
        book,
        BookUpdate(
            title="New Title",
            author="New Author",
            description="anything",
        ),
    )

    assert updated.title == "New Title"
    assert updated.author == "New Author"

    refreshed = await BooksDAO.get_by_id(async_session, book.id)
    assert refreshed is not None
    assert refreshed.title == "New Title"
    assert refreshed.author == "New Author"


@pytest.mark.asyncio
async def test_delete(async_session, owner_user):
    category = Category(name=f"test-category-{uuid.uuid4()}")
    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    book = Book(
        title="To Delete",
        author="Author",
        description="anything",
        owner_id=owner_user.id,
        category_id=category.id,
    )
    book = await BooksDAO.create(async_session, book)

    await BooksDAO.delete(async_session, book)

    missing = await BooksDAO.get_by_id(async_session, book.id)
    assert missing is None
