import pytest_asyncio
from aiohttp import ClientSession


@pytest_asyncio.fixture(name='client_session', scope='session')
async def client_session():
    client_session = ClientSession()
    yield client_session
    await client_session.close()


@pytest_asyncio.fixture(name='make_get_request')
def make_get_request(client_session: ClientSession):
    async def inner(url, params: dict = None):
        async with client_session.get(url, params=params) as response:
            body = await response.json()
            headers = response.headers
            status = response.status

            return body, headers, status

    return inner
