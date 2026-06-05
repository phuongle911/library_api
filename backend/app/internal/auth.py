import os

from fastapi import Header, HTTPException
from starlette import status as http_status

INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "dev-internal-token")

async def verify_internal_token(
        x_internal_token: str | None = Header(default=None),
):
    if x_internal_token != INTERNAL_API_TOKEN:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal token",
        )
