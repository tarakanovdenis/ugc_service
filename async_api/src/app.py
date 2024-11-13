from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from src.api.v1 import films, persons, genres
from src.core.config import settings
from src.db import elastic, redis


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Connect to redis and elastic
    redis.redis = Redis(
        host=settings.redis_settings.redis_host,
        port=settings.redis_settings.redis_port
    )
    elastic.es = AsyncElasticsearch(
        hosts=[
            settings.es_settings.elasticsearch_host,
        ],
    )
    yield
    # close redis and elastic
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title=settings.project_settings.title,
    docs_url=settings.project_settings.docs_url,
    openapi_url=settings.project_settings.openapi_url,
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
