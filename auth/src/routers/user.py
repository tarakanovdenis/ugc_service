from typing import Any

from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
)
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from redis.asyncio import Redis
from fastapi_pagination import Page, paginate

from src.db.postgres import db_helper
from src.db.redis import get_redis
from src.schemas.user import (
    UserRead,
    UserUpdate,
    UserUpdatePassword,
    UserResetPassword,
    UserEmail,
)
from src.schemas.login_history import LoginHistoryBase
from src.models.user import User
from src.models.user_roles import DefaultRoleEnum
from src.models.login_history import LoginHistory
from src.utils import user_crud, auth_utils
from src.utils.messages import messages
from src.utils.decorators import permission_required


router = APIRouter()


@router.get("/info", response_model=UserRead | Any)
@permission_required(role_required=DefaultRoleEnum.PUBLIC_USER)
async def get_auth_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.http_bearer),
    payload: dict = Depends(auth_utils.get_current_token_payload),
    user: User = Depends(auth_utils.get_current_auth_user),
    redis: Redis = Depends(get_redis),
):
    """
    Get user information:

    Return value:
    - **user** (UserRead): user with the following
        fields: id, login, first_name, last_name and email
    """
    token_id = payload["jti"]
    if await redis.get(token_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_ERROR,
        )

    return user


@router.get("/login_history/", response_model=Page[LoginHistoryBase])
@permission_required(role_required=DefaultRoleEnum.PUBLIC_USER)
async def get_auth_user_auth_history(
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.http_bearer),
    payload: dict = Depends(auth_utils.get_current_token_payload),
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(db_helper.get_session),
):
    """
    Get authentication history:

    Parameters:
    - **page** (int): page number (default=1)
    - **size** (ing): page size (default=50) - the amount
        of authentication history rows

    Return value:
    - **items** (list[LoginHistoryBase]): list of user authentication
        history with the following fields: OS, browser, logged in at
    - **total** (int): the amount of authentication history rows
    - **page** (int): page number
    - **size** (int): page size
    - **pages** (int): the amount of pages
    """

    token_id = payload["jti"]

    if await redis.get(token_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_ERROR,
        )

    user_id = payload["user_id"]

    stmt = select(LoginHistory).where(LoginHistory.user_id == user_id)
    result: Result = await session.execute(stmt)
    login_history = result.scalars().all()

    return paginate(login_history)


@router.patch("/update", response_model=UserRead)
@permission_required(role_required=DefaultRoleEnum.PUBLIC_USER)
async def update_user_partially(
    user_update: UserUpdate,
    payload: dict = Depends(auth_utils.get_current_token_payload),
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.http_bearer),
    session: AsyncSession = Depends(db_helper.get_session),
):
    """
    Update user partially:

    Return value:
    - **user** (UserRead): user with the following
        fields: id, login, first_name, last_name and email
    """
    user_id = payload["user_id"]
    user = await user_crud.get_user_by_id(user_id, session=session)
    return await user_crud.update_user(
        session=session, user=user, user_update=user_update
    )


@router.post("/change-password", status_code=status.HTTP_202_ACCEPTED)
@permission_required(role_required=DefaultRoleEnum.PUBLIC_USER)
async def change_password(
    password_data: UserUpdatePassword,
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.http_bearer),
    user: User = Depends(auth_utils.get_current_auth_user),
    session: AsyncSession = Depends(db_helper.get_session),
):
    """
    Change user password

    Parameters:
    - **password_data** (UserUpdatePassword): old, new and confirming new password
        passwords
    """
    return await user_crud.update_user_password(session, user, password_data)


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    email_data: UserEmail, session: AsyncSession = Depends(db_helper.get_session)
):
    """
    Send reset password token to the user

    Parameters:
    - **email** (UserEmail): user email
    """
    return await user_crud.forgot_user_password(
        email_data.email,
        session,
    )


@router.post("/reset-password/{token}", status_code=status.HTTP_202_ACCEPTED)
async def reset_password(
    token: str,
    password_data: UserResetPassword,
    session: AsyncSession = Depends(db_helper.get_session),
) -> UserRead | Any:
    """
    Reset user password using using reset password token

    Parameters:
    - **token** (str): reset password token
    - **password_data** (UserResetPassword): new, confirming new password passwords
    """
    return await user_crud.reset_user_password(
        token,
        password_data,
        session,
    )


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
@permission_required(role_required=DefaultRoleEnum.PUBLIC_USER)
async def delete_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.http_bearer),
    user: User = Depends(auth_utils.get_current_auth_user),
    session: AsyncSession = Depends(db_helper.get_session),
) -> None:
    """
    Delete user
    """
    await user_crud.delete_user(session=session, user=user)
