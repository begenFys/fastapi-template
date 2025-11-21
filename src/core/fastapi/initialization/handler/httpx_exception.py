"""HTTPX Exception."""

from httpx import HTTPStatusError
from loguru import logger

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from src.core.helper.scheme.response.error import ErrorResponse


def init_orjson_for_httpx_exception(
    app_: FastAPI,
    loguru_logger: bool = False,
) -> None:
    """Init handler for HTTPStatusError."""

    @app_.exception_handler(HTTPStatusError)
    async def exception_handler(
        request: Request,
        exc: HTTPStatusError,
    ) -> ORJSONResponse:
        if loguru_logger:
            logger.exception(exc)

        return ORJSONResponse(
            status_code=exc.response.status_code,
            content=ErrorResponse(
                error_code=exc.response.status_code,
                detail=exc.response.text,
            ).model_dump(),
        )
