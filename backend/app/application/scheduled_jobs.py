import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import update

from app.core.database import async_session_maker
from app.models.reservation import Reservation

logger = logging.getLogger(__name__)


async def expire_old_reservations() -> None:
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=30)

    async with async_session_maker() as db:
        result = await db.execute(
            update(Reservation)
            .where(
                Reservation.status == "pending",
                Reservation.created_at < cutoff_time,
                )
            .values(
                status="expired",
                updated_at=datetime.now(timezone.utc),
                )
            )
        await db.commit()
        logger.info( "expired pending reservations",
                    extra={"expired_count" : result.rowcount},)
        

async def run_scheduler() -> None:
    while True:
        try:
            await expire_old_reservations()
        except Exception:
            logger.exception("Scheduled reservation cleanup failed")

            await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(run_scheduler())
