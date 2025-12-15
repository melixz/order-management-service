from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.order_management_service.models.user import User
from src.order_management_service.repositories.user_repository import UserRepository
from src.order_management_service.schemas.user import UserCreate, UserLogin
from src.order_management_service.schemas.auth import Token
from src.order_management_service.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)


async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    repo = UserRepository(db)

    existing_user = await repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_password = get_password_hash(user_data.password)
    user = await repo.create_user(
        email=user_data.email,
        hashed_password=hashed_password,
    )
    return user


async def authenticate_user(db: AsyncSession, login_data: UserLogin) -> Token:
    repo = UserRepository(db)

    user = await repo.get_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)
