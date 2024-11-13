from typing import Annotated
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    status,
    Depends,
    Form,
    Request,
    Path,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from redis.asyncio import Redis

from src.utils import auth_token_utils
from src.schemas.user import UserCreate
from src.schemas.token import Token
from src.db.postgres import db_helper
from src.db.redis import get_redis
from src.models.user import User
from src.models.refresh_token import RefreshToken
from src.utils import user_crud, auth_utils
from src.utils.decorators import rate_limit
from src.utils.messages import messages


router = APIRouter()


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, session: AsyncSession = Depends(db_helper.get_session)
):
    """
    Create user:

    Return value:
    - **user** (UserRead): user with the following
        fields: username, first_name, last_name and email
    """
    return await user_crud.create_user(session, user_in)


@router.post("/login/")
@rate_limit()
async def login(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(db_helper.get_session),
):
    """
    Login user by username and password forms:

    Parameters:
    - **username** (str): user username
    - **password** (str): user password

    Return value:
    - **token** (Token): token with the following fields:
        access_token, refresh_token, token_type
    """
    user: User = await auth_utils.get_user_by_username_or_raise_exception(
        username, password, session
    )

    await auth_utils.parse_request_user_agent_information(request, session, user)

    access_token = await auth_token_utils.create_access_token(user, session)
    refresh_token = await auth_token_utils.create_refresh_token(user, session)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    redis: Redis = Depends(get_redis),
    payload: dict = Depends(auth_utils.get_current_token_payload),
    session: AsyncSession = Depends(db_helper.get_session),
):
    """
    Logout user
    """
    user_id = payload["user_id"]
    first_name = payload["first_name"]
    last_name = payload["last_name"]

    token_id = payload["jti"]
    token_expires_in = int(payload["exp"] - datetime.now(timezone.utc).timestamp() + 3)

    stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
    await session.execute(stmt)
    await session.commit()

    await redis.setex(
        token_id,
        token_expires_in,
        f"User(user_id={user_id}, first_name={first_name}, "
        f"last_name={last_name}, logout_at={datetime.now()})",
    )


@router.post("/refresh/", response_model=Token)
async def get_auth_refresh_jwt(
    user: User = Depends(auth_utils.get_current_auth_user_for_refresh),
    session: AsyncSession = Depends(db_helper.get_session),
) -> Token:
    """
    Refresh access and refresh tokens
    """
    access_token = await auth_token_utils.create_access_token(user, session)
    refresh_token = await auth_token_utils.create_refresh_token(user, session)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/subscription/user/{user_id}/create",
)
async def create_user_subscription(
    user_id: Annotated[str, Path(description="User ID (UUID4)")],
    session: AsyncSession = Depends(db_helper.get_session),
):
    user: User = await user_crud.get_user_by_id(
        user_id,
        session,
    )
    user.is_subscriber = True
    await session.commit()
    return {
        "details": messages.SUBSCRIPTION_WAS_ASSIGNED_TO_THE_USER,
    }


@router.post(
    "/subscription/user/{user_id}/delete/",
)
async def cancel_user_subscription(
    user_id: Annotated[str, Path(description="User ID (UUID4)")],
    session: AsyncSession = Depends(db_helper.get_session),
):
    user: User = await user_crud.get_user_by_id(
        user_id,
        session,
    )
    user.is_subscriber = False
    await session.commit()
    return {
        "details": messages.USER_SUBSCRIPTION_WAS_CANCELLED,
    }
