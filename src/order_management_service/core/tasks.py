import asyncio

from taskiq import TaskiqScheduler
from taskiq_redis import RedisStreamBroker

from src.order_management_service.core.settings import REDIS_URL

broker = RedisStreamBroker(url=REDIS_URL)
scheduler = TaskiqScheduler(broker)


@broker.task
async def process_order_task(order_id: str) -> None:
    await asyncio.sleep(2)
    print(f"Order {order_id} processed")
