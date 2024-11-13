from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.models import *


async def get_mongodb_client(
    mongodb_host: str,
    mongodb_port: int,
    mongodb_db_name: str,
):
    client = AsyncIOMotorClient(
        host=mongodb_host,
        port=mongodb_port,
        uuidRepresentation='standard'
    )
    db = client[mongodb_db_name]
    await init_beanie(
        database=db,
        document_models=[
            FilmWork,
            Review,
            Rating,
            Bookmark,
        ]
    )
