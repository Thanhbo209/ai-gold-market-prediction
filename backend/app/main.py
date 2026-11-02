from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.predictions import router as predictions_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    # CORS configuration – public API, no credentials needed
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # could be restricted via env var if needed
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(predictions_router)

    return app


app = create_app()
