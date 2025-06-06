import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from eav_backend import migrate
from eav_backend.config import settings
from eav_backend.database import SessionLocal
from eav_backend.routes.v1 import admin_routes, asset_routes
from eav_backend.services.dynamic_model_service import DynamicModelService
from eav_backend.services.entity_definition_service import EntityDefinitionService
from eav_backend.services.entity_import_service import EntityImportService


logging.config.dictConfig(settings.logging_config)
logger = logging.getLogger("openepi")
logger.info(f"LogLevel is set to {settings.log_level}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    session = SessionLocal()
    try:
        eds = EntityDefinitionService(session)
        EntityImportService(eds).import_entities()
        DynamicModelService(eds, app).build_models_from_entity_definitions()
    finally:
        session.close()
    yield


def get_application() -> FastAPI:
    api = FastAPI(lifespan=lifespan, root_path=settings.api_root_path)

    if settings.enable_assets:
        api.include_router(asset_routes.router)

    if settings.enable_admin_api:
        api.include_router(admin_routes.router)

    if settings.enable_metrics:
        Instrumentator().instrument(api).expose(api)

    return api


if settings.run_migrations:
    logger.info("Running database migrations")
    migrate.run_migrations(
        schemas=[settings.postgres_schema],
        connection_string=settings.database_connection,
        script_location=settings.alembic_directory,
        alembic_file=settings.alembic_file,
    )

app = get_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "eav_backend.__main__:app",
        host=settings.uvicorn_host,
        port=settings.uvicorn_port,
        reload=settings.uvicorn_reload,
        proxy_headers=settings.uvicorn_proxy_headers,
    )
