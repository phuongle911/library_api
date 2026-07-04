import asyncio
import json
from datetime import datetime

import redis.asyncio as redis

from app.core.database import AsyncSessionLocal
from app.infrastructure.repositories.borrow_history_read_repository import (
    BorrowHistoryReadRepository,
)
from app.application.cache import delete_cache


REDIS_URL = "redis://redis:6379"
CHANNEL_NAME = "library_events"


async def handle_book_borrowed(payload: dict):
    await asyncio.sleep(5)

    async with AsyncSessionLocal() as db:
        async with db.begin():
            existing = await BorrowHistoryReadRepository.get_by_borrow_record_id(
                db=db,
                borrow_record_id=payload["borrow_record_id"],
            )

            if existing:
                return

            await BorrowHistoryReadRepository.create(
                db=db,
                borrow_record_id=payload["borrow_record_id"],
                user_id=payload["user_id"],
                book_id=payload["book_id"],
                book_title=payload["book_title"],
                borrow_status=payload["status"],
                borrowed_at=datetime.fromisoformat(payload["borrowed_at"]),
            )
            await delete_cache(
                key=f"borrow_history:user:{payload['user_id']}",
            )


async def handle_book_returned(payload: dict):
    async with AsyncSessionLocal() as db:
        async with db.begin():
            read_model = (
                await BorrowHistoryReadRepository.get_by_borrow_record_id(
                    db=db,
                    borrow_record_id=payload["borrow_record_id"],
                )
            )

            if not read_model:
                return
            
            await BorrowHistoryReadRepository.update_status(
                db=db,
                read_model=read_model,
                status="returned",
                returned_at=datetime.fromisoformat(
                    payload["returned_at"]
                ),
            )
            await delete_cache(
                key=f"borrow_history:user:{payload['user_id']}",
            )


async def main():
    print("Read model consumer started")

    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )

    pubsub = redis_client.pubsub()

    await pubsub.subscribe(CHANNEL_NAME)

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        event = json.loads(message["data"])

        if event["event_type"] == "BookBorrowed":
            await handle_book_borrowed(event["payload"])

        elif event["event_type"] == "BookReturned":
            await handle_book_returned(event["payload"])

if __name__ == "__main__":
    asyncio.run(main())
