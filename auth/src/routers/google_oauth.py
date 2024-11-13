from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from src.utils.social_auth import SocialAuthMainpage
from src.db.postgres import db_helper

from src.utils.social_auth import (
    OAuthProviders,
    get_authorize_redirect,
    authorize_access_token,
    get_or_create_user
)


router = APIRouter()


@router.get('/')
async def oauth_main_page(request: Request):
    social_auth_provider_object = SocialAuthMainpage(request)
    return social_auth_provider_object.mainpage()


@router.get('/{auth_provider}/login')
async def login(
    request: Request,
    auth_provider: Annotated[
        OAuthProviders,
        Path(
            description=(
                f'OAuth Provider can be selected from '
                f'the following: `{OAuthProviders.GOOGLE.value}`.'
                )
        )
    ],
):
    return await get_authorize_redirect(
        auth_provider,
        request
    )


@router.get('/google/auth')
async def auth(
    request: Request,
    session: AsyncSession = Depends(db_helper.get_session)
):
    '''
    Google OAuth2 endpoint.
    '''
    token = await authorize_access_token(request, OAuthProviders.GOOGLE.value)

    return await get_or_create_user(token, session)