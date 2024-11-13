from http import HTTPStatus

import pytest_asyncio
from aiohttp import ClientSession


@pytest_asyncio.fixture(name='client_session', scope='session')
async def client_session():
    client_session = ClientSession()
    yield client_session
    await client_session.close()


@pytest_asyncio.fixture(name='make_get_request')
def make_get_request(client_session: ClientSession):
    async def inner(url, headers: dict, params: dict = None):
        async with client_session.get(
            url, headers=headers,
            params=params
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
            return body, headers, status
    return inner


@pytest_asyncio.fixture(name='make_post_request')
def make_post_request(client_session: ClientSession):
    async def inner(
        url,
        data: dict = None,
        params: dict = None,
        headers: dict = None,
        json: dict = None,
    ):
        async with client_session.post(
            url,
            data=data,
            params=params,
            headers=headers,
            json=json,
        ) as response:
            body = await response.json()
            headers = response.headers
            status = response.status
            return body, headers, status
    return inner


@pytest_asyncio.fixture(name='get_authentication_token')
def get_authentication_token(client_session: ClientSession):
    async def inner():
        creation_user_data = {
            "username": "tarakanovdenis",
            "password": "string",
            "first_name": "Denis",
            "last_name": "Tarakanov",
            "email": "tarakanov021098@gmail.com"
        }

        authentication_data = {
            'username': creation_user_data['username'],
            'password': creation_user_data['password']
        }

        async with client_session.post(
            'http://backend_for_auth:8000' + '/auth/auth/login',
            data=authentication_data
        ) as response:
            body = await response.json()

            if body == {'detail': 'Invalid username or password'}:
                async with client_session.post(
                    'http://backend_for_auth:8000' + '/auth/users/register',
                    json=creation_user_data
                ) as response:
                    if response.status == HTTPStatus.CREATED:
                        async with client_session.post(
                            'http://backend_for_auth:8000' + '/auth/auth/login',
                            data=authentication_data
                        ) as response:
                            body = await response.json
                            return body['access_token']
            return body['access_token']
    return inner
