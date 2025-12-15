import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.order_management_service.core.database import Base, get_db
from src.order_management_service.core.rate_limiter import rate_limiter_dependency
from src.order_management_service.main import app
from src.order_management_service.services import order_service as order_service_module


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, future=True)
TestingSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def _create_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _drop_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session


async def _noop_rate_limiter() -> None:
    return None


async def _fake_send_new_order_event(
    order_id: str,
    user_id: int,
    total_price: float,
    status: str,
    items: list[dict],
) -> None:
    return None


_ORDER_CACHE: dict[str, str] = {}


async def _fake_get_order_from_cache(order_id: str) -> str | None:
    return _ORDER_CACHE.get(order_id)


async def _fake_set_order_to_cache(
    order_id: str,
    data: str,
    ttl_seconds: int = 300,
) -> None:
    _ORDER_CACHE[order_id] = data


async def _fake_invalidate_order_cache(order_id: str) -> None:
    _ORDER_CACHE.pop(order_id, None)


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[rate_limiter_dependency] = _noop_rate_limiter

order_service_module.send_new_order_event = _fake_send_new_order_event
order_service_module.get_order_from_cache = _fake_get_order_from_cache
order_service_module.set_order_to_cache = _fake_set_order_to_cache
order_service_module.invalidate_order_cache = _fake_invalidate_order_cache


@pytest.fixture(scope="function")
def client() -> TestClient:
    asyncio.run(_drop_db())
    asyncio.run(_create_db())
    with TestClient(app) as c:
        yield c
    asyncio.run(_drop_db())
