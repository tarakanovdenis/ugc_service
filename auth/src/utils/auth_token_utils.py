from uuid import uuid4
from datetime import datetime, timezone, timedelta

import jwt
# from jwt.exceptions import ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.user import User
from src.models.refresh_token import RefreshToken
from src.models.user_roles import DefaultRoleEnum
# from src.utils.messages import messages


def encode_jwt(
    payload: dict,
    key: str = settings.jwt_settings.private_key_path.read_text(),
    algorithm: str = settings.jwt_settings.algorithm,
    expire_minutes: int = settings.jwt_settings.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(payload=to_encode, key=key, algorithm=algorithm)
    return encoded


def decode_jwt(
    jwt_token: str | bytes,
    key: str = settings.jwt_settings.public_key_path.read_text(),
    algorithm: str = settings.jwt_settings.algorithm,
):
    # try:
    decoded = jwt.decode(jwt_token, key=key, algorithms=[algorithm])
    # except ExpiredSignatureError:
    #     return {
    #         'detail': messages.TOKEN_IS_EXPIRED_OR_USER_IS_INACTIVE
    #     }
    return decoded


TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_jwt_token(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.jwt_settings.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


async def create_access_token(
    user: User,
    session: AsyncSession,
) -> str:

    user_role_list = []

    if user.is_active:
        user_role_list.append(DefaultRoleEnum.PUBLIC_USER.value)

    if user.is_staff:
        user_role_list.append(DefaultRoleEnum.ADMIN.value)

    if user.is_superuser:
        user_role_list.append(DefaultRoleEnum.SUPER_USER.value)

    token_id = str(uuid4())

    jwt_payload = {
        "sub": user.username,
        "user_id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": " ".join(user_role_list),
        "jti": token_id,
    }
    return create_jwt_token(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.jwt_settings.access_token_expire_minutes,
    )


async def create_refresh_token(user: User, session: AsyncSession) -> str:
    token_id = str(uuid4())
    jwt_payload = {
        "sub": user.username,
        "user_id": str(user.id),
        "jti": token_id,
    }

    token = create_jwt_token(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(minutes=5),
    )
    token_to_db = RefreshToken(id=token_id, user_id=user.id)
    session.add(token_to_db)
    await session.commit()
    await session.refresh(token_to_db)
    return token


async def create_reset_password_token(
    email: str,
    user_is_active: bool,
):
    token_id = str(uuid4())
    payload = {
        "email": email,
        "is_active": user_is_active,
        "jti": token_id,
    }
    return encode_jwt(
        payload,
        expire_minutes=settings.jwt_settings.reset_password_token_expire_minutes,
    )


async def return_email_if_token_is_verified(token: str):
    payload: dict = decode_jwt(token)
    email = payload.get("email")
    exp_in = payload.get("exp")
    is_active = payload.get("is_active")
    if bool(datetime.now(timezone.utc).timestamp() < exp_in and is_active):
        return email
