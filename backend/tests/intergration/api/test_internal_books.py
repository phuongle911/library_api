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


async def test_reserve_book_internal_success(
        client,
        sample_book,
):
    response = await client.post(
        f"/api/v1/internal/books/{sample_book.id}/reserve",
        headers={"X-Internal-Token": "dev-internal-token"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["book_id"] == sample_book.id
    assert data["available_copies"] == sample_book.available_copies

async def test_reserve_book_internal_without_token_returns_401(
        client,
        sample_book,
):
    response = await client.post(
        f"/api/v1/internal/books/{sample_book.id}/reserve"
    )

    assert response.status_code == 401

async def test_reserve_book_internal_not_found(client):
    response = await client.post(
        "/api/v1/internal/books/99999/reserve",
        headers={"X-Internal-Token": "dev-internal-token",},
    )

    assert response.status_code == 404

async def test_reserve_book_internal_not_available(
        client,
        sample_book,
):
    sample_book.available_copies = 0

    response = await client.post(
        f"/api/v1/internal/books/{sample_book.id}/reserve",
        headers={"X-Internal-Token": "dev-internal-token"},
    )

    assert response.status_code == 400
    # assert response.json()["detail"] == "Book not available"
    print(response.status_code)
    print(response.json())

async def test_release_book_inernal_success(
        client,
        sample_book,
):
    original_copies = sample_book.available_copies

    response = await client.post(
        f"/api/v1/internal/books/{sample_book.id}/release",
        headers={"X-Internal-Token": "dev-internal-token"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["book_id"] == sample_book.id
    assert data["available_copies"] == original_copies + 1

async def test_release_book_internal_without_token_returns_401(
        client,
        sample_book,
):
    response = await client.post(
        f"/api/v1/internal/books/{sample_book.id}/release"
    )

    assert response.status_code == 401

async def test_release_book_internal_not_found(client):
    response = await client.post(
        "/api/v1/internal/books/99999/release",
        headers={"X-Internal-Token": "dev-internal-token"},
    )

    assert response.status_code == 404
