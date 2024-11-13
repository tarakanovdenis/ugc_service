from datetime import datetime, timezone

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from uaparser import UAParser

from src.models.user import User
from src.models.login_history import LoginHistory
from src.utils.messages import messages
from src.utils import auth_token_utils
from src.db.postgres import db_helper


http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


unauth_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=messages.INVALID_USERNAME_OR_PASSWORD,
    headers={'WWW-Authenticate': 'Basic'}
)


def get_current_token_payload(
    token: str = Depends(http_bearer)
) -> dict:
    try:
        _, credentials = token
        payload = auth_token_utils.decode_jwt(
            credentials[1]
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_ERROR
        )
    return payload


async def get_current_auth_user(
    session: AsyncSession = Depends(db_helper.get_session),
    payload: dict = Depends(get_current_token_payload),
):
    id = payload['user_id']
    token_type = payload.get(auth_token_utils.TOKEN_TYPE_FIELD)

    if token_type != auth_token_utils.ACCESS_TOKEN_TYPE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_TYPE,
        )

    stmt = select(User).where(User.id == id)
    result: Result = await session.execute(stmt)
    user: User = result.scalars().first()

    return user


async def get_current_auth_user_for_refresh(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.get_session)
):
    id = payload['user_id']
    token_type = payload.get(auth_token_utils.TOKEN_TYPE_FIELD)

    if token_type != auth_token_utils.REFRESH_TOKEN_TYPE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.INVALID_TOKEN_TYPE,
        )
    stmt = select(User).where(User.id == id)
    result: Result = await session.execute(stmt)
    user: User = result.scalar()
    return user


async def parse_request_user_agent_information(
    request: Request,
    session: AsyncSession,
    user: User,
):
    ua_header_data = request.headers.get('User-Agent')
    login_device_information = UAParser.parse(ua_header_data)

    if not login_device_information['device']['type']:
        login_device_information['device']['type'] = 'undefined'

    entry_history_to_db = LoginHistory(
        OS=(
            f"{login_device_information['os']['name']} "
            f"{login_device_information['os']['version']}"
        ),
        browser=(
            f"{login_device_information['browser']['name']} "
        ),
        device_type=login_device_information['device']['type'],
        logged_in_at=datetime.now(timezone.utc),
        user_id=user.id
    )

    session.add(entry_history_to_db)
    await session.commit()
    await session.refresh(entry_history_to_db)


async def get_user_by_username_or_raise_exception(
    username: str,
    password: str,
    session: AsyncSession
):
    stmt = select(User).where(User.username == username)
    result: Result = await session.execute(stmt)
    user: User | None = result.scalar()

    if not user:
        raise unauth_exception

    if not user.verify_password(
        plain_password=password,
        hashed_password=user.password
    ):
        raise unauth_exception

    return user
