from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.order_management_service.core.database import get_db
from src.order_management_service.core.rate_limiter import RateLimiter
from src.order_management_service.schemas.auth import Token
from src.order_management_service.schemas.user import UserCreate, UserResponse
from src.order_management_service.services.auth_service import (
    authenticate_user,
    register_user,
)


auth_router = APIRouter(
    prefix="",
    tags=["auth"],
)


DbSession = Annotated[AsyncSession, Depends(get_db)]


@auth_router.post(
    "/register/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    db: DbSession,
) -> UserResponse:
    user = await register_user(db, user_data)
    return UserResponse.model_validate(user)


@auth_router.post(
    "/token/",
    response_model=Token,
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
    _: None = RateLimiter,
) -> Token:
    return await authenticate_user(
        db,
        login_data=type(
            "Login", (), {"email": form_data.username, "password": form_data.password}
        )(),  # minimal wrapper
    )
