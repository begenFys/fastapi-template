"""FastAPI handler exceptions."""

from loguru import logger

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from src.core.helper.scheme.response.error import ErrorResponse


def init_orjson_for_exception(app_: FastAPI, loguru_logger: bool = True) -> None:
    """Init handler for Exception."""

    @app_.exception_handler(Exception)
    async def exception_handler(
        request: Request,
        exc: Exception,
    ) -> ORJSONResponse:
        status_code, detail = 500, f"{exc.__class__}: {repr(exc)}"

        if loguru_logger:
            logger.exception(
                repr(exc),
            )

        return ORJSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                error_code=status_code,
                detail=detail,
            ).model_dump(),
        )
