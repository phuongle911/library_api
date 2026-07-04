import json
import redis.asyncio as redis

REDIS_URL = "redis://redis:6379"

redis_client = redis.from_url(
    REDIS_URL,
    decode_response=True,
)


async def get_cache(key: str):
    value = await redis_client.get(key)

    if not value:
        return None
    
    return json.loads(value)


async def set_cache(key: str, value, ttl_seconds: int = 60):
    await redis_client.set(
        key,
        json.dumps(value, default=str),
        ex=ttl_seconds,
    )


async def delete_cache(key: str):
    await redis_client.delete(key)
