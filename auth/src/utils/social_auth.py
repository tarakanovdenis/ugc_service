import json
from enum import Enum

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.responses import HTMLResponse, JSONResponse

from src.models.user_social_account import UserSocialAccount
from src.schemas.user import UserSocialAccountRead
from src.utils.auth_token_utils import create_access_token
from src.models.user import User
from src.core.config import settings


oauth = OAuth()
oauth.register(
    name=settings.oauth_settings.oauth_provider,
    server_metadata_url=settings.oauth_settings.oauth_google_server_metadata_url,
    client_id=settings.oauth_settings.oauth_client_id,
    client_secret=settings.oauth_settings.oauth_client_secret,
    client_kwargs={
        'scope': 'openid email profile'
    }
)


class OAuthProviders(Enum):
    # YANDEX = 'yandex'
    GOOGLE = 'google'


OAUTH_REDIRECT_URI = 'auth'


class SocialAuthMainpage:
    def __init__(self, request):
        self.email = None
        self.request = request

    def mainpage(self):

        user = self.request.session.get('user')

        if user:
            data = json.dumps(user)
            html_template = (
                f'<pre>{data}</pre>'
                '<a href="/logout">logout</a>'
            )
            return HTMLResponse(html_template)

        return HTMLResponse('<a href="/oauth/google/login">Google Login</a>')

    async def user_data(self, email, session: AsyncSession):
        self.email = email
        stmt = select(User).where(User.email == email)
        result: Result = await session.execute(stmt)
        user: User | None = result.scalar()

        return user


async def get_authorize_redirect(
    auth_provider: OAuthProviders,
    request: Request
):
    redirect_uri = request.url_for(OAUTH_REDIRECT_URI)
    if auth_provider.value == OAuthProviders.GOOGLE.value:
        return await oauth.google.authorize_redirect(request, redirect_uri)


async def authorize_access_token(
    request: Request,
    auth_provider: str
):
    try:
        if auth_provider == OAuthProviders.GOOGLE.value:
            token = await oauth.google.authorize_access_token(request)
            return token
    except OAuthError as error:
        return HTMLResponse(f'There was an error: {error}')


async def get_or_create_user(token, session: AsyncSession):
    '''
    Get or create user fetching user info from token.
    '''
    user_info = token.get('userinfo')

    stmt = select(User).where(User.email == user_info['email'])
    result: Result = await session.execute(stmt)
    user: User | None = result.scalar()

    if user:
        access_token = await create_access_token(
            user=user,
            session=session
        )
        return JSONResponse(
            {
                'message': 'Login successful',
                'access_token': access_token
            }
        )
    else:
        user = UserSocialAccount(
            first_name=user_info['given_name'],
            last_name=user_info['family_name'],
            email=user_info['email']
        )
        access_token = await create_access_token(
            user=user,
            session=session
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        user_dto = UserSocialAccountRead.model_validate(
            user, from_attributes=True
        )

        user_json = user_dto.model_dump_json()

        return JSONResponse(
            {
                'message': (
                    'User was successfully created by fetching'
                    'data from user\'s social account'
                ),
                'user': user_json,
                'access_token': access_token
            }
        )
