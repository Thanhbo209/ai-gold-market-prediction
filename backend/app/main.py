from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.predictions import router as predictions_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.include_router(health_router)
    app.include_router(predictions_router)

    return app


app = create_app()
