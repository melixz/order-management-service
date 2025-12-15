from redis.asyncio import Redis

from src.order_management_service.core.settings import REDIS_URL

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)


async def get_order_from_cache(order_id: str) -> str | None:
    return await redis_client.get(f"order:{order_id}")


async def set_order_to_cache(order_id: str, data: str, ttl_seconds: int = 300) -> None:
    await redis_client.setex(f"order:{order_id}", ttl_seconds, data)


async def invalidate_order_cache(order_id: str) -> None:
    await redis_client.delete(f"order:{order_id}")
