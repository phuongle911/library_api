import pytest


@pytest.mark.asyncio
async def test_endpoint_requires_authentication(client):
    response_get_list_book = await client.get("/api/v1/books")

    assert response_get_list_book.status_code == 401


@pytest.mark.asyncio
async def test_list_books_with_auth(client, auth_headers):
    response = await client.get("/api/v1/books", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert "meta" in data
    assert isinstance(data["items"], list)

    # meta = data["meta"]
    # assert isinstance(response.json(), list)
