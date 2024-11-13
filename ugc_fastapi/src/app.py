from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.core.logger import LoggingMiddleware
from src.db.mongodb import get_mongodb_client
from src.routers.film_work import router as film_work_router
from src.routers.review import router as review_router
from src.routers.rating import router as rating_router
from src.routers.bookmark import router as bookmark_router
from src.services import rabbitmq


@asynccontextmanager
async def lifespan(_: FastAPI):
    await get_mongodb_client(
        settings.mongodb_host,
        settings.mongodb_port,
        settings.mongodb_db_name,
    )
    rabbitmq.setup_rabbitmq()
    yield
    # client.close()


application = FastAPI(
    lifespan=lifespan,
    title='Film\'s API',
    docs_url='/ugc_fastapi/docs',
    openapi_url='/ugc_fastapi/api/openapi.json',
    description='Film\'s API Service',
    version='0.1.0'
)
application.include_router(film_work_router, tags=['Films'], prefix='/ugc_fastapi/films')
application.include_router(review_router, tags=['Reviews'], prefix='/ugc_fastapi/reviews')
application.include_router(rating_router, tags=['Ratings'], prefix='/ugc_fastapi/ratings')
application.include_router(bookmark_router, tags=['Bookmarks'], prefix='/ugc_fastapi/bookmarks')

application.add_middleware(LoggingMiddleware)
