import json
import os
from redis.asyncio import Redis


class RedisEventPublisher:
    def __init__(self):
        self.redis = Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            decode_responses=True,
        )

    async def publish(self, stream: str, event: dict):
        await self.redis.xadd(
            stream,
            {"data": json.dumps(event)},
        )
