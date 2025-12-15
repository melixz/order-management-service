import asyncio
import json

from aiokafka import AIOKafkaConsumer

from src.order_management_service.core.settings import KAFKA_BOOTSTRAP_SERVERS
from src.order_management_service.core.tasks import process_order_task


async def consume_new_orders() -> None:
    consumer = AIOKafkaConsumer(
        "new_order",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        enable_auto_commit=True,
        auto_offset_reset="earliest",
    )

    await consumer.start()
    try:
        async for message in consumer:
            payload = message.value
            order_id = str(payload.get("order_id"))
            await process_order_task.kiq(order_id=order_id)
    finally:
        await consumer.stop()


def run_consumer() -> None:
    asyncio.run(consume_new_orders())
