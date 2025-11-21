"""Функции жизненного цикла для FastAPI приложения."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Never

from fastapi import FastAPI
from loguru import logger

from src.api import main_router
from src.core.fastapi.initialization.handler import (
    init_handler_for_custom_http_exception,
    init_handler_for_exception,
    init_handler_for_httpx_exception,
    init_handler_for_sqlalchemy_exception,
)
from src.core.logger import setup_loguru


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[Never]:
    """Функция жизненного цикла FastAPI приложения(startup и shutdown новый)."""
    setup_loguru()
    logger.debug("Loguru started.")

    init_handler_for_custom_http_exception(app_=app, loguru_logger=True)
    init_handler_for_httpx_exception(app_=app, loguru_logger=True)
    init_handler_for_exception(app_=app, loguru_logger=True)
    init_handler_for_sqlalchemy_exception(app_=app, loguru_logger=True)
    logger.debug("Handler initialized.")

    app.include_router(router=main_router)
    logger.debug("Main API router initialized")

    yield  # type: ignore[misc]
