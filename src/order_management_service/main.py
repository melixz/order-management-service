from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.order_management_service.api.auth import auth_router
from src.order_management_service.api.orders import orders_router

app = FastAPI(
    title="Order Management Service",
    description="Сервис управления заказами",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(orders_router)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get(
    "/health",
    summary="Проверка здоровья сервиса",
    tags=["system"],
)
async def health_check() -> dict:
    return {"status": "healthy"}
