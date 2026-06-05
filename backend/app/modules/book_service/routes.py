import logging
import httpx
from starlette import status as http_status
from fastapi import APIRouter, Depends, Query, HTTPException  # API library
from sqlalchemy.ext.asyncio import AsyncSession  # database library
from app.modules.book_service.schemas import BookCreate, BookUpdate, BookResponse  # schemas/DTO layer
from app.core.database import get_db, get_read_db  # DB/engine layer
from app.modules.book_service.service import (
    create_book_service,
    get_book_service,
    list_books_service,
    update_book_service,
    delete_book_service
    )  # service layer
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import PaginatedResponse, BookOut
from app.modules.borrow_service.contracts.book_contract import BookContract
from app.modules.borrow_service.clients.book_client import INTERNAL_API_BASE_URL, INTERNAL_API_TOKEN


logger = logging.getLogger("app.books")

book_router = APIRouter()


@book_router.post("/books", response_model=BookResponse, status_code=201)
async def create_book(
    payload: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
      ):
    return await create_book_service(db, payload, current_user)


@book_router.get("/books", response_model=PaginatedResponse[BookOut])
async def list_books(
    title: str | None = Query(default=None),
    author: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    sort_dir: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_read_db),
    current_user: User = Depends(get_current_user),
):
    return await list_books_service(
        db=db,
        current_user=current_user.id,
        title=title,
        author=author,
        category_id=category_id,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )


@book_router.get("/books/{book_id}", response_model=BookResponse, status_code=200)
async def get_book(
    self,
    db,
    book_id: int,
) -> BookContract | None:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{INTERNAL_API_BASE_URL}/internal/books/{book_id}",
                headers={"X-Internal-Token": INTERNAL_API_TOKEN},
            )

            if response.status_code == 404:
                return None
            
            response.raise_for_statuc()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=http_status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Book service timeout",
        )
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Book service unavailable",
        )
    
    data = response.json()

    return BookContract(
        id=data["id"],
        title=data["title"],
        available_copies=data["available_copies"],
    )


@book_router.put("/books/{book_id}", response_model=BookResponse, status_code=200)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await update_book_service(db, book_id, payload, current_user)


@book_router.delete("/books/{book_id}", status_code=204)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
      ):
    return await delete_book_service(db, book_id, current_user)
