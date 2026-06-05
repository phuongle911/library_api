from starlette import status as http_status


async def test_get_internal_book_sucess(
        client,
        sample_book,
):
    response = await client.get(
        f"/api/v1/internal/books/{sample_book.id}",
        headers={"X-Internal-Token": "dev-internal-token"},
    )

    assert response.status_code == http_status.HTTP_200_OK

    data = response.json()
    assert data["id"] == sample_book.id
    assert data["title"] == sample_book.title
    assert data["available_copies"] == sample_book.available_copies


async def test_get_internal_book_without_token_returns_401(client, sample_book):
    response = await client.get(
        f"/api/v1/internal/books/{sample_book.id}",
    )

    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
