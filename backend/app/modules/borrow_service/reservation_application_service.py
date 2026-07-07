from app.modules.borrow_service.reservation_repository import ReservationRepository


class ReservationApplicationService:
    def __init__(self, reservation_repository: ReservationRepository):
        self.reservation_repository = reservation_repository

    async def reserve_book(
            self,
            user_id: int,
            book_id: int,
    ):
        existing = await self.reservation_repository.get_pending_reservation(
            user_id=user_id,
            book_id=book_id,
        )

        if existing:
            raise ValueError("You already have a pending reservation for this book.")
        
        return await self.reservation_repository.create_pending_reservation(
            user_id=user_id,
            book_id=book_id,
        )
        
    async def get_my_reservations(
            self,
            user_id: int,
    ):
        return await self.reservation_repository.list_user_reservations(
            user_id=user_id,
        )
