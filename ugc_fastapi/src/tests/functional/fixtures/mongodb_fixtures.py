import pytest_asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.models import *
from src.tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='mongo_client', scope='function', autouse=True)
async def setup_mongodb_client():
    client = AsyncIOMotorClient(
        host=test_settings.mongodb_host,
        port=test_settings.mongodb_port,
        uuidRepresentation='standard'
    )
    db = client[test_settings.mongodb_db_name]
    await init_beanie(
        database=db,
        document_models=[
            FilmWork,
            Review,
            Rating,
            Bookmark,
        ]
    )
    yield
    client.drop_database(db)
    client.close()
