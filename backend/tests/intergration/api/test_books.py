import pytest


@pytest.mark.asyncio
async def test_endpoint_requires_authentication(client):
    payload = {
        "title": "Test Book",
        "description": "a book description",
        "author": "Author Name"}
    response_get_list_book = await client.get("/api/v1/books")
    response_create_book = await client.post("/api/v1/books", json=payload)
    response_get_book = await client.get("/api/v1/books/1")
    response_update_book = await client.put("/api/v1/books/1", json=payload)
    response_delete_book = await client.delete("/api/v1/books/1")
    assert response_get_list_book.status_code == 401
    assert response_create_book.status_code == 401
    assert response_get_book.status_code == 401
    assert response_update_book.status_code == 401
    assert response_delete_book.status_code == 401


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
