import os
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from unittest.mock import Mock
from sqlalchemy import text

from app.main import app
from app.core.database import Base, get_db, get_read_db
from app.models.user import User
from app.core.config import settings
from app.core.rate_limit import reset_rate_limit
from app.models.books import Book
from app.models.categories import Category
from app.models.borrow_record import BorrowRecord
from app.models.refresh_token import RefreshToken
from app.models.idempotency_key import IdempotencyKey
from app.models.job import Job


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def clear_rate_limit_state():
    reset_rate_limit()
    yield
    reset_rate_limit()

async def _ensure_test_database_exists() -> None:
    test_url = settings.TEST_DATABASE_URL
    admin_url = test_url.rsplit("/", 1)[0] + "/postgres"
    db_name = test_url.rsplit("/", 1)[-1]

    engine = create_async_engine(
        admin_url,
        future=True,
        poolclass=NullPool,
        isolation_level="AUTOCOMMIT",
        )
    try:
        async with engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            )
            if exists is None:
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def prepare_test_database():
    await _ensure_test_database_exists()
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        future=True,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def _truncate_all_tables(engine) -> None:
    table_names = ", ".join(
        f'"{table.name}"' for table in Base.metadata.sorted_tables
    )
    if not table_names:
        return
    async with engine.begin() as conn:
        await conn.execute(
            text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE")
        )


@pytest_asyncio.fixture
async def async_engine(prepare_test_database):
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        future=True,
        poolclass=NullPool,
    )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    AsyncSessionLocal = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await _truncate_all_tables(async_engine)


@pytest_asyncio.fixture
async def client(async_session):
    async def override_get_db():
        yield async_session

    async def override_get_read_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_read_db] = override_get_read_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def owner_user(async_session):
    u = User(
        name="Test Owner",
        email=f"owner_{uuid.uuid4()}@example.com",
        hashed_password="fake-hash",
        is_active=True,
        role="user",
    )
    async_session.add(u)
    await async_session.commit()
    await async_session.refresh(u)
    return u


@pytest_asyncio.fixture
async def other_owner_user(async_session):
    u = User(
        name="Ann",
        email=f"other_{uuid.uuid4()}@gmail.com",
        hashed_password="fake-hash",
        is_active=True,
        role="user",
    )
    async_session.add(u)
    await async_session.commit()
    await async_session.refresh(u)
    return u


@pytest_asyncio.fixture
async def auth_headers(client):
    email = f"user_{uuid.uuid4()}@example.com"
    password = "password123"
    role = "user"

    await client.post(
        "/api/v1/auth/signup",
        json={"name": "Test User", "email": email, "password": password, "role": role},
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def set_execute_first(db, first_value):
    result = Mock()
    scalars = Mock()
    scalars.first.return_value = first_value
    result.scalars.return_value = scalars
    db.execute.return_value = result


@pytest.fixture
async def sample_book(async_session):
    book = Book(
        title="Clean Code",
        available_copies=3,
    )

    async_session.add(book)
    await async_session.commit()
    await async_session.refresh(book)

    return book


@pytest.fixture
async def sample_category(async_session):
    category = Category(name="Programming")

    async_session.add(category)
    await async_session.commit()
    await async_session.refresh(category)

    return category


@pytest.fixture
async def sample_book(async_session, owner_user, sample_category):
    book = Book(
        title="Clean Code",
        description="Software craftsmanship book",
        author="Robert Martin",
        owner_id=owner_user.id,
        category_id=sample_category.id,
        available_copies=3,
    )

    async_session.add(book)
    await async_session.commit()
    await async_session.refresh(book)

    return book
