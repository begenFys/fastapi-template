"""SQLAlchemy Exception."""

from asyncpg import UniqueViolationError  # type: ignore[import-untyped]
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from loguru import logger
from sqlalchemy.exc import IntegrityError

from src.core.helper.scheme.response.error import ErrorResponse
from src.core.helper.type.exception import LogSeverity


def init_handler_for_sqlalchemy_exception(
    app_: FastAPI,
    loguru_logger: bool = False,
) -> None:
    """Init handler for SQLAlchemy Exceptions."""

    def resolve_sqlalchemy_exception(
        request: Request,
        exc: IntegrityError,
    ) -> tuple[int, str, str]:
        status_code = 500
        detail = "Error with query to database."
        severity = LogSeverity.error

        try:
            if exc.orig is not None:
                if isinstance(exc.orig.__cause__, UniqueViolationError):
                    status_code = 409
                    severity = LogSeverity.warning
                    msg = exc._message()
                    if (detail_index := msg.find("DETAIL:")) != -1:
                        detail = msg[detail_index + len("DETAIL:") :].strip()
        except Exception as internal_exc:
            logger.exception(repr(internal_exc))
            status_code = 500
            severity = LogSeverity.error
            detail = "Parsing error with log from database"

        return status_code, detail, severity

    @app_.exception_handler(IntegrityError)
    async def exception_handler(
        request: Request,
        exc: IntegrityError,
    ) -> ORJSONResponse:
        status_code, detail, severity = resolve_sqlalchemy_exception(
            request=request,
            exc=exc,
        )
        if loguru_logger:
            logger.exception(repr(exc))
            logger.log(severity, detail)
        return ORJSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                error_code=status_code,
                detail=detail,
            ).model_dump(),
        )
