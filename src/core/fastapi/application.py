"""Билдинг FastAPI приложения."""

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.core.fastapi.lifespan import lifespan
from src.core.fastapi.middleware import LoguruMiddleware
from src.core.setting import EnvironmentType, project_info, settings


def get_app() -> FastAPI:
    """Получить FastAPI приложение.

    Это главный конструктов приложения.

    Returns:
        FastAPI приложение
    """
    app = FastAPI(
        title=project_info.get_project_name(),
        version=project_info.get_project_version(),
        docs_url=None
        if settings.ENVIRONMENT == EnvironmentType.PRODUCTION
        else "/api/docs",
        redoc_url=None
        if settings.ENVIRONMENT == EnvironmentType.PRODUCTION
        else "/api/redoc",
        openapi_url=None
        if settings.ENVIRONMENT == EnvironmentType.PRODUCTION
        else "/api/openapi.json",
        default_response_class=ORJSONResponse,
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=[
                    "GET",
                    "OPTIONS",
                    "POST",
                    "PATCH",
                    "PUT",
                    "DELETE",
                ],
                allow_headers=["*"],
            ),
            # Middleware(
            #     SQLAlchemyMiddleware,
            # ),
            Middleware(
                LoguruMiddleware,
            ),
        ],
        lifespan=lifespan,
    )
    return app
