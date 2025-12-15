import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.order_management_service.core.kafka import send_new_order_event
from src.order_management_service.core.redis import (
    get_order_from_cache,
    set_order_to_cache,
    invalidate_order_cache,
)
from src.order_management_service.models.order import Order
from src.order_management_service.repositories.order_repository import OrderRepository
from src.order_management_service.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderUpdateStatus,
)


async def create_order(
    db: AsyncSession,
    user_id: int,
    order_data: OrderCreate,
) -> Order:
    repo = OrderRepository(db)

    total_price = order_data.total_price
    items_payload = [item.model_dump() for item in order_data.items]

    order = await repo.create_order(
        user_id=user_id,
        items=items_payload,
        total_price=total_price,
    )

    await send_new_order_event(
        order_id=str(order.id),
        user_id=user_id,
        total_price=order.total_price,
        status=order.status.value,
        items=items_payload,
    )

    response = OrderResponse.model_validate(order)
    await set_order_to_cache(str(order.id), json.dumps(response.model_dump()))

    return order


async def get_order_by_id(db: AsyncSession, order_id: UUID) -> OrderResponse:
    cached = await get_order_from_cache(str(order_id))
    if cached:
        data = json.loads(cached)
        return OrderResponse(**data)

    repo = OrderRepository(db)
    order = await repo.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    response = OrderResponse.model_validate(order)
    await set_order_to_cache(str(order_id), json.dumps(response.model_dump()))
    return response


async def update_order_status(
    db: AsyncSession,
    order_id: UUID,
    status_data: OrderUpdateStatus,
) -> OrderResponse:
    repo = OrderRepository(db)

    order = await repo.update_status(order_id, status_data.status)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    await invalidate_order_cache(str(order_id))

    response = OrderResponse.model_validate(order)
    await set_order_to_cache(str(order_id), json.dumps(response.model_dump()))
    return response


async def get_user_orders(db: AsyncSession, user_id: int) -> list[Order]:
    repo = OrderRepository(db)
    return await repo.get_by_user_id(user_id)
