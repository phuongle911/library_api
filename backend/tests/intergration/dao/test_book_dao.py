import pytest
from sqlalchemy import select

from app.DAO.books_dao import BooksDAO
from app.models.books import Book
from app.schemas.books import BookCreate, BookUpdate
from tests.conftest import async_session


@pytest.mark.asyncio
async def test_create_and_get_by_id(async_session, owner_user):
    owner_id = owner_user.id

    created = await BooksDAO.create(
        async_session, 
        BookCreate(title="Clean Code", author="Robert Martin", description="anything"), 
        owner_id=owner_id,
        )
    
    fetched = await BooksDAO.get_by_id(async_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Clean Code"
    assert fetched.author == "Robert Martin"
    assert fetched.owner_id == owner_id


@pytest.mark.asyncio
async def test_get_by_title(async_session):
    owner_id = 1

    await BooksDAO.create(
        async_session,
        BookCreate(title="Deep Work", author="Cal Newport", description="anything"),
        owner_id = owner_id,
    )

    found = await BooksDAO.get_by_title(async_session, "Deep Work")
    assert found is not None
    assert found.title == "Deep Work"
    assert found.author == "Cal Newport"

    not_found = await BooksDAO.get_by_title(async_session, "Does Not Exist")
    assert not_found is None


@pytest.mark.asyncio
async def test_list_by_owner_filters_and_sort(async_session, owner_user, other_owner_user):
    owner_id = owner_user.id
    other_owner_id = other_owner_user.id

    await BooksDAO.create(
        async_session, 
        BookCreate(title="Alpha", author="Zed", description="anything"), 
        owner_id
        )
    
    await BooksDAO.create(
        async_session, 
        BookCreate(title="Beta", author="Alice", description="anything"), 
        owner_id
        )
    
    await BooksDAO.create(
        async_session, 
        BookCreate(title="Gamma", author="Bob", description="anything"), 
        owner_id
        )
    
    await BooksDAO.create(
        async_session, 
        BookCreate(title="Alpha (other)", author="Zed", description="anything"), 
        other_owner_id
        )
    
    items = await BooksDAO.list_by_owner(async_session, owner_id=owner_id, title="a")
    assert all(i.owner_id == owner_id for i in items)
    assert all("a" in i.title.lower() for i in items)

    items = await BooksDAO.list_by_owner(async_session, owner_id=owner_id, author="bo")
    assert len(items) == 1
    assert items[0].author == "Bob"

    items = await BooksDAO.list_by_owner(async_session, owner_id=owner_id, sort_by="title")
    assert [b.title for b in items] == sorted([b.title for b in items])

    items = await BooksDAO.list_by_owner(async_session, owner_id=owner_id, sort_by="newest")
    ids = [b.id for b in items]
    assert ids == sorted(ids, reverse=True)


@pytest.mark.asyncio
async def test_list_by_owner_paginated(async_session, owner_user):
    owner_id = owner_user.id

    for i in range(1, 26):
        await BooksDAO.create(
            async_session,
            BookCreate(title=f"Book {i:02d}", author="Author", description="anything"),
            owner_id=owner_id
        )

    items, total = await BooksDAO.list_by_owner_paginated(
        async_session,
        owner_id=owner_id,
        page=1,
        page_size=10,
    )

    assert total == 25
    assert len(items) == 10

    ids = [b.id for b in items]
    assert ids == sorted(ids, reverse=True)

    items, total = await BooksDAO.list_by_owner_paginated(
        async_session,
        owner_id=owner_id,
        page=3,
        page_size=10,
    )

    assert total == 25
    assert len(items) == 5

    items, total = await BooksDAO.list_by_owner_paginated(
        async_session,
        owner_id=owner_id,
        sort_by="title",
        sort_dir="asc",
        page=1,
        page_size=10,
    )

    titles = [b.title for b in items]
    assert titles == sorted(titles)


@pytest.mark.asyncio
async def test_update(async_session, owner_user):
    owner_id = owner_user.id
    book = await BooksDAO.create(
        async_session,
        BookCreate(title="Old Title", author="Old Author", description="anything"),
        owner_id=owner_id,
    )

    updated = await BooksDAO.update(
        async_session, 
        book, 
        BookUpdate(title="New Title", author="New Author", description="anything")
        )
    
    assert updated.title == "New Title"
    assert updated.author == "New Author"


    #verify from DB
    refreshed = await BooksDAO.get_by_id(async_session, book.id)
    assert refreshed is not None
    assert refreshed.title == "New Title"


@pytest.mark.asyncio
async def test_delete(async_session):
    owner_id = 1
    book = await BooksDAO.create(
        async_session,
        BookCreate(title="To Delete", author="XO", description="anything"),
        owner_id=owner_id,
    )

    await BooksDAO.delete(async_session, book)

    missing = await BooksDAO.get_by_id(async_session, book.id)
    assert missing is None

    #optionsal: confirm table doesn't include it
    result = await async_session.execute(select(Book).where(Book.id == book.id))
    assert result.scalar_one_or_none() is None


