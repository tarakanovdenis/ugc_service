from typing import Annotated

from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
    Path,
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
    UserUpdate
)
from src.schemas.login_history import LoginHistoryBase
from src.models.user import User
from src.models.user_roles import DefaultRoleEnum
from src.models.login_history import LoginHistory
from src.utils import user_crud, auth_utils
from src.utils.messages import messages
from src.utils.decorators import permission_required


router = APIRouter()


@router.get('/users', response_model=list[UserRead])
@permission_required(role_required=DefaultRoleEnum.ADMIN)
async def get_users(
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.http_bearer),
    session: AsyncSession = Depends(db_helper.get_session)
):
    '''
    Get user list:

    Return value:
    - **users** (list[UserRead]): list of users with the following
        fields: id, login, first_name, last_name and email
    '''
    return await user_crud.get_users(session)


@router.get('/user/{user_id}', response_model=UserRead)
@permission_required(role_required=DefaultRoleEnum.ADMIN)
async def get_user(
    user_id: Annotated[str, Path(description='User ID')],
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.http_bearer),
    session: AsyncSession = Depends(db_helper.get_session)
):
    '''
    Get user by id:

    Parameters:
    - **user_id** (str): user ID (UUID)

    Return value:
    - **user** (UserRead): user with the following
        fields: id, login, first_name, last_name and email
    '''
    return await user_crud.get_user_by_id(user_id, session)


@router.get('/auth_history/{user_id}', response_model=Page[LoginHistoryBase])
@permission_required(role_required=DefaultRoleEnum.ADMIN)
async def get_user_auth_history(
    user_id: Annotated[str, Path(description='User ID')],
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.http_bearer),
    payload: dict = Depends(auth_utils.get_current_token_payload),
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(db_helper.get_session)
):
    '''
    Get user authentication history by user id:

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
    '''

    token_id = payload['jti']

    if await redis.get(token_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_ERROR
        )

    stmt = select(LoginHistory).where(LoginHistory.user_id == user_id)

    result: Result = await session.execute(stmt)
    login_history = result.scalars().all()

    return paginate(login_history)


@router.patch('/{user_id}/', response_model=UserRead)
@permission_required(role_required=DefaultRoleEnum.ADMIN)
async def update_user_partially(
    user_update: UserUpdate,
    user: Annotated[User, Depends(user_crud.get_user_by_id)],
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.http_bearer),
    session: AsyncSession = Depends(db_helper.get_session)
):
    '''
    Update user partially by user id:

    Parameters:
    - **user_id** (str): user id

    Return value:
    - **user** (UserRead): user with the following
        fields: id, login, first_name, last_name and email
    '''
    return await user_crud.update_user(
        session=session,
        user=user,
        user_update=user_update
    )


@router.delete('/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
@permission_required(role_required=DefaultRoleEnum.ADMIN)
async def delete_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.http_bearer),
    user: User = Depends(user_crud.get_user_by_id),
    session: AsyncSession = Depends(db_helper.get_session)
) -> None:
    '''
    Delete user by user id:

    Parameters:
    - **user_id** (str): user id
    '''
    await user_crud.delete_user(
        session=session,
        user=user
    )
