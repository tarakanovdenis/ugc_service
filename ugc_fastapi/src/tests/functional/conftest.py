import asyncio

import pytest_asyncio


pytest_plugins = [
    'src.tests.functional.fixtures.mongodb_fixtures',
    'src.tests.functional.fixtures.make_request_fixtures',
]


@pytest_asyncio.fixture(name='event_loop', scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
