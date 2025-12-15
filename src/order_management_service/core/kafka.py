import json

from aiokafka import AIOKafkaProducer

from src.order_management_service.core.settings import KAFKA_BOOTSTRAP_SERVERS


async def _get_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()
    return producer


async def send_new_order_event(
    order_id: str,
    user_id: int,
    total_price: float,
    status: str,
    items: list[dict],
) -> None:
    producer = await _get_producer()
    try:
        payload = {
            "order_id": order_id,
            "user_id": user_id,
            "total_price": total_price,
            "status": status,
            "items": items,
        }
        await producer.send_and_wait("new_order", value=payload)
    finally:
        await producer.stop()
