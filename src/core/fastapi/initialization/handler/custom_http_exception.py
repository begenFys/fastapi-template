"""CustomHTTPException."""

from loguru import logger

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from src.core.exception.base import CustomHTTPException


def init_orjson_for_custom_http_exception(
    app_: FastAPI,
    loguru_logger: bool = True,
) -> None:
    """Инициализация слушателя для CustomHTTPException."""

    @app_.exception_handler(CustomHTTPException)
    async def custom_http_exception_handler(
        request: Request,
        exc: CustomHTTPException,
    ) -> ORJSONResponse:
        if loguru_logger and exc.status_code >= 500:
            logger.error(
                exc.detail,
            )

        return ORJSONResponse(
            status_code=exc.status_code,
            content=exc.as_dict(),
        )
