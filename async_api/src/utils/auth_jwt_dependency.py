import jwt
from fastapi import (
    status,
    HTTPException,
    Request
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.config import settings


def decode_jwt(
    jwt_token: str | bytes,
    key: str = settings.jwt_settings.public_key_path.read_text(),
    algorithm: str = settings.jwt_settings.algorithm
) -> dict | None:
    decoded_jwt = jwt.decode(
        jwt_token,
        key=key,
        algorithms=[algorithm]
    )
    return decoded_jwt


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid authorization code.'
            )

        if not credentials.scheme == 'Bearer':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Only Bearer token might be accepted.'
            )

        decoded_token = self.parse_token(credentials.credentials)

        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid or expired token.'
            )

        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> dict | None:
        return decode_jwt(jwt_token)


security_jwt = JWTBearer()