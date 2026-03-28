import os
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from unittest.mock import Mock

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or "postgresql+asyncpg://postgres:postgres@db:5432/app_test"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def prepare_test_database():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_engine(prepare_test_database):
    engine = create_async_engine(
        TEST_DATABASE_URL,
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


@pytest_asyncio.fixture
async def client(async_session):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

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

    await client.post(
        "/api/v1/auth/signup",
        json={"name": "Test User", "email": email, "password": password},
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