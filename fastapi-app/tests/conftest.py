import pytest
from httpx import AsyncClient
import sys
import os

sys.path.append(os.path.abspath("."))
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        app=app,
        base_url="http://test",
        ) as ac: 
        yield ac