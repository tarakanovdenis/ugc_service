from typing import Annotated
from datetime import datetime, timezone

from fastapi import Depends, Path, status, HTTPException
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import ExpiredSignatureError

from src.models.user import User
from src.schemas.user import (
    UserCreate,
    UserRead,
    UserUpdate,
    UserUpdatePassword,
    UserResetPassword,
)
from src.db.postgres import db_helper
from src.services import rabbitmq
from src.utils.messages import messages
from src.utils import auth_token_utils


async def get_users(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.username)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return users


async def get_user(session: AsyncSession, user_id: str) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_id(
    user_id: Annotated[str, Path],
    session: AsyncSession = Depends(db_helper.get_session),
) -> User:
    user = await get_user(session, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )

    return user


async def get_user_by_email(
    email: str,
    session: AsyncSession,
) -> User:
    stmt = select(User).where(User.email == email)
    result: Result = await session.execute(stmt)
    user = result.scalars().one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.USER_NOT_FOUND,
        )
    return user


async def create_user(session: AsyncSession, user_in: UserCreate) -> UserRead:
    user = User(**user_in.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)

    await rabbitmq.send_message_using_routing_key(
        exchange_name=rabbitmq.UserActivityExchange.EXCHANGE_NAME.value,
        routing_key=rabbitmq.UserActivityExchange.REGISTRATION_ACTIVITY_ROUTING_KEY.value,
        message={
            "user_id": str(user.id),
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "timestamp": datetime.now(timezone.utc).strftime("%d-%m-%YYYY %H:%M:%S %z"),
        },
    )
    return user


async def update_user(
    session: AsyncSession, user: User, user_update: UserUpdate
) -> UserRead:
    for name, value in user_update.model_dump(exclude_unset=True).items():
        if name == "password":
            value = user.get_hashed_password(value)
        setattr(user, name, value)
    await session.commit()
    return user


async def delete_user(
    session: AsyncSession,
    user: User,
) -> None:
    await session.delete(user)
    await session.commit()


async def update_user_password(
    session: AsyncSession,
    user: User,
    password_data: UserUpdatePassword,
) -> None:

    if not user.verify_password(password_data.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.OLD_PASSWORD_IS_INCORRECT,
        )

    if not password_data.new_password == password_data.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.PASSWORDS_DO_NOT_MATCH,
        )

    setattr(user, "password", user.get_hashed_password(password_data.new_password))

    await session.commit()
    return {
        "detail": messages.PASSWORD_UPDATED,
    }


async def forgot_user_password(
    email: str,
    session: AsyncSession,
):
    user: User = await get_user_by_email(email, session)
    reset_password_token = await auth_token_utils.create_reset_password_token(
        user.email, user.is_active,
    )

    await rabbitmq.send_message_using_routing_key(
        exchange_name=rabbitmq.UserActivityExchange.EXCHANGE_NAME.value,
        routing_key=rabbitmq.UserActivityExchange.PASSWORD_RESET_ACTIVITY_ROUTING_KEY.value,
        message={
            "reset_password_token": reset_password_token,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "timestamp": datetime.now(timezone.utc).strftime("%d-%m-%YYYY %H:%M:%S %z"),
        },
    )
    return {
        "detail": messages.CHECK_RESET_PASSWORD_TOKEN_EMAIL,
    }


async def reset_user_password(
    token: str,
    password_data: UserResetPassword,
    session: AsyncSession,
):
    try:
        email = await auth_token_utils.return_email_if_token_is_verified(token)
    except ExpiredSignatureError:
        return {"detail": messages.TOKEN_IS_EXPIRED_OR_USER_IS_INACTIVE}

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.TOKEN_IS_EXPIRED_OR_USER_IS_INACTIVE,
        )

    if not password_data.new_password == password_data.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.PASSWORDS_DO_NOT_MATCH,
        )

    user: User = await get_user_by_email(email, session)

    user.password = user.get_hashed_password(password_data.new_password)

    await session.commit()
    return user
