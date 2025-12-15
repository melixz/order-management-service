from uuid import UUID

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.order_management_service.models.order import Order, OrderStatus


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self,
        user_id: int,
        items: list[dict],
        total_price: float,
    ) -> Order:
        order = Order(
            user_id=user_id,
            items=items,
            total_price=total_price,
        )
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_by_id(self, order_id: UUID) -> Order | None:
        query: Select[tuple[Order]] = select(Order).where(Order.id == order_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        order_id: UUID,
        status: OrderStatus,
    ) -> Order | None:
        query = (
            update(Order)
            .where(Order.id == order_id)
            .values(status=status)
            .returning(Order)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> list[Order]:
        query: Select[tuple[Order]] = select(Order).where(Order.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
