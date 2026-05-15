import time
from fastapi import HTTPException

REQUESTS = {}

MAX_REQUESTS = 5
WINDOW_SECONDS = 60

async def check_rate_limit(ip: str):
    now = time.time()

    requests = REQUESTS.get(ip, [])

    requests = [
        ts for ts in requests
        if now - ts < WINDOW_SECONDS
    ]

    if len(requests) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
        )
    
    requests.append(now)

    REQUESTS[ip] = requests
    