from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from redis.asyncio import Redis
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from src.db import redis
from src.routers.auth import router as auth_router
from src.routers.admin import router as admin_router
from src.routers.user import router as user_router
from src.routers.google_oauth import router as oauth_router
from src.core.config import settings
from src.utils.tracer_config import configure_tracer


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis.redis = Redis(
        host=settings.service_settings.redis_host,
        port=settings.service_settings.redis_port,
        db=1
    )
    yield
    await redis.redis.close()


if settings.service_settings.jaeger_configure_tracer:
    configure_tracer()


application = FastAPI(
    lifespan=lifespan,
    title=settings.project_settings.title,
    docs_url=settings.project_settings.docs_url,
    openapi_url=settings.project_settings.openapi_url,
    description=settings.project_settings.description,
    version=settings.project_settings.version,
)
application.add_middleware(SessionMiddleware, secret_key="some secret text")

add_pagination(application)

application.include_router(
    admin_router, prefix='/auth/admin', tags=['Admin Endpoints']
)
application.include_router(
    auth_router, prefix='/auth', tags=['Auth Endpoints']
)
application.include_router(
    user_router, prefix='/auth/user', tags=['User Endpoints']
)
application.include_router(
    router=oauth_router,
    prefix="/oauth",
    tags=["OAuth2 Endpoints"],
)

origins = [
    "*",
]

application.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

print(settings.service_settings.jaeger_configure_tracer)
if settings.service_settings.jaeger_configure_tracer:

    FastAPIInstrumentor.instrument_app(application)

    @application.middleware('http')
    async def before_request(request: Request, call_next):
        response = await call_next(request)
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={'detail': 'X-Request-Id is required'}
            )
        return response
