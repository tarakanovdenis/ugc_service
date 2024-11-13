import pytest_asyncio
from redis.asyncio import Redis

from src.tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='redis_client', scope='session')
async def redis_client():
    redis_client = Redis(
        host=test_settings.redis_host,
        port=test_settings.redis_port
    )
    yield redis_client
    await redis_client.close()
