from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reservation import Reservation


class ReservationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_pending_reservation(
            self,
            user_id: int,
            book_id: int,
    ) -> Reservation:
        reservation = Reservation(
            user_id=user_id,
            book_id=book_id,
            status="pending",
        )

        self.db.add(reservation)
        await self.db.flush()
        await self.db.refresh(reservation)
        return reservation
    
    async def get_pending_reservation(
            self,
            user_id: int,
            book_id: int,
    ) -> Reservation | None:
        result = await self.db.execute(
            select(Reservation).where(
                Reservation.user_id == user_id,
                Reservation.book_id == book_id,
                Reservation.status == "pending",
            )
        )

        return result.scalar_one_or_none()
    
    async def list_user_reservations(
            self,
            user_id: int,
    ) -> list[Reservation]:
        result = await self.db.execute(
            select(Reservation).where(
                Reservation.user_id == user_id)
                .order_by(Reservation.created_at.desc())
            )
        
        return list(result.scalars().all())
