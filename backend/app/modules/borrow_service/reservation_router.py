from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.borrow_service.reservation_application_service import ReservationApplicationService
from app.modules.borrow_service.reservation_repository import ReservationRepository
from app.modules.borrow_service.reservation_schemas import ReservationCreateRequest, ReservationResponse
from app.core.dependencies import get_current_user

reservation_router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"],
)

def get_reservation_service(
        db: AsyncSession = Depends(get_db),
) -> ReservationApplicationService:
    repository = ReservationRepository(db)
    return ReservationApplicationService(repository)

@reservation_router.post("", response_model=ReservationResponse)
async def reserve_book(
    request: ReservationCreateRequest,
    current_user=Depends(get_current_user),
    service: ReservationApplicationService = Depends(get_reservation_service),
):

    return await service.reserve_book(
        user_id=current_user.id,
        book_id=request.book_id,
    )

@reservation_router.get("", response_model=list[ReservationResponse])
async def get_my_reservations(
    current_user=Depends(get_current_user),
    service: ReservationApplicationService = Depends(get_reservation_service),
):
    
    return await service.get_my_reservations(
        user_id=current_user.id,
    )
