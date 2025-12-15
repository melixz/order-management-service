from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.order_management_service.models.order import OrderStatus


class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderCreate(BaseModel):
    items: list[OrderItem]
    total_price: float


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: UUID
    user_id: int
    items: list[OrderItem]
    total_price: float
    status: OrderStatus
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
