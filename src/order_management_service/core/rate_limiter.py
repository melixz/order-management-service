from fastapi import Depends, HTTPException, Request, status

from src.order_management_service.core.redis import redis_client
from src.order_management_service.core.settings import (
    RATE_LIMIT_WINDOW_SECONDS,
    RATE_LIMIT_REQUESTS,
)


async def rate_limiter_dependency(request: Request) -> None:
    client_ip = request.client.host
    key = f"rate:{client_ip}"

    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, RATE_LIMIT_WINDOW_SECONDS)

    if current > RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
        )


RateLimiter = Depends(rate_limiter_dependency)
