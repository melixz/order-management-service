from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.order_management_service.core.database import get_db
from src.order_management_service.core.rate_limiter import RateLimiter
from src.order_management_service.core.security import get_current_user
from src.order_management_service.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderUpdateStatus,
)
from src.order_management_service.services.order_service import (
    create_order,
    get_order_by_id,
    get_user_orders,
    update_order_status,
)


orders_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@orders_router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_endpoint(
    order_data: OrderCreate,
    db: DbSession,
    current_user: CurrentUser,
    _: None = RateLimiter,
) -> OrderResponse:
    order = await create_order(
        db=db,
        user_id=current_user["id"],
        order_data=order_data,
    )
    return OrderResponse.model_validate(order)


@orders_router.get(
    "/{order_id}/",
    response_model=OrderResponse,
)
async def get_order_endpoint(
    order_id: UUID,
    db: DbSession,
    _current_user: CurrentUser,
) -> OrderResponse:
    order = await get_order_by_id(db, order_id)
    return order


@orders_router.patch(
    "/{order_id}/",
    response_model=OrderResponse,
)
async def update_order_status_endpoint(
    order_id: UUID,
    status_data: OrderUpdateStatus,
    db: DbSession,
    _current_user: CurrentUser,
) -> OrderResponse:
    updated = await update_order_status(
        db=db,
        order_id=order_id,
        status_data=status_data,
    )
    return updated


@orders_router.get(
    "/user/{user_id}/",
    response_model=list[OrderResponse],
)
async def get_user_orders_endpoint(
    user_id: int,
    db: DbSession,
    _current_user: CurrentUser,
) -> list[OrderResponse]:
    orders = await get_user_orders(db, user_id)
    return [OrderResponse.model_validate(order) for order in orders]
