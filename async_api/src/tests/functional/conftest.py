import asyncio

import pytest_asyncio
# from elasticsearch import AsyncElasticsearch
# from elasticsearch.helpers import async_bulk
# from aiohttp import ClientSession
# from redis.asyncio import Redis

# from src.tests.functional.settings import test_settings


pytest_plugins = [
    'src.tests.functional.fixtures.elastic_fixtures',
    'src.tests.functional.fixtures.redis_fixtures',
    'src.tests.functional.fixtures.make_request_fixtures',
]


@pytest_asyncio.fixture(name='event_loop', scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# @pytest_asyncio.fixture(name='redis_client', scope='session')
# async def redis_client():
#     redis_client = Redis(
#         host=test_settings.redis_host,
#         port=test_settings.redis_port
#     )
#     yield redis_client
#     await redis_client.close()


# @pytest_asyncio.fixture(name='es_client', scope='session')
# async def es_client():
#     es_client = AsyncElasticsearch(
#         hosts=f'http://{test_settings.es_host}:{test_settings.es_port}',
#         verify_certs=False
#     )
#     yield es_client
#     await es_client.close()


# @pytest_asyncio.fixture(name='es_write_data')
# def es_write_data(es_client: AsyncElasticsearch):
#     async def inner(
#         es_index,
#         es_index_mappings,
#         es_index_settings,
#         data: list[dict]
#     ):
#         if await es_client.indices.exists(index=es_index):
#             await es_client.indices.delete(index=es_index)

#         await es_client.indices.create(
#             index=es_index,
#             mappings=es_index_mappings,
#             settings=es_index_settings
#         )

#         updated, errors = await async_bulk(
#             client=es_client,
#             actions=data,
#             refresh='wait_for'
#         )

#         if errors:
#             raise Exception('Ошибка записи данных в Elasticsearch')

#     return inner


# @pytest_asyncio.fixture(name='client_session', scope='session')
# async def client_session():
#     client_session = ClientSession()
#     yield client_session
#     await client_session.close()


# @pytest_asyncio.fixture(name='make_get_request')
# def make_get_request(client_session: ClientSession):
#     async def inner(url, params: dict = None):
#         async with client_session.get(url, params=params) as response:
#             body = await response.json()
#             headers = response.headers
#             status = response.status

#             return body, headers, status

#     return inner
