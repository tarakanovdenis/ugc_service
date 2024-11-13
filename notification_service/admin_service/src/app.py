from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.core.config import settings
from src.api.v1.for_admin import router as admin_panel_router
from src.api.v1.for_services import router as third_party_service_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url='/notification_admin/api/openapi',
    openapi_url='/notification_admin/api/openapi.json',
    description='Admin Panel for the Notification Service',
    default_response_class=ORJSONResponse,
    version='0.1.0'
)
app.include_router(
    admin_panel_router,
    prefix='/notification_admin/api/v1/admin',
    tags=['Sending notifications']
)
app.include_router(
    third_party_service_router,
    prefix='/notification_admin/api/v1/services',
    tags=['Sending notifications from third-party services']
)
