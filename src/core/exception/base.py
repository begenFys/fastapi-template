"""Кастомные ошибки для handler и responses."""
# ruff: noqa: D101

from http import HTTPStatus
from typing import Any

from fastapi.exceptions import HTTPException

from src.core.helper.scheme.response.error import ErrorResponse


class CustomHTTPException(HTTPException):
    """Родитель кастомного HTTP исключения."""

    def __init__(
        self,
        status_code: int,
        detail: str = "Ошибка сервера",
    ):
        self.status_code = status_code
        self.detail = detail

    def as_dict(self) -> dict[str, Any]:
        """Представление ошибки как dict."""
        return ErrorResponse(
            error_code=self.status_code,
            detail=self.detail,
        ).model_dump()


class InternalServerException(CustomHTTPException):
    def __init__(self, message: str = "Ошибка сервера"):
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=message,
        )


class BadRequestException(CustomHTTPException):
    def __init__(
        self,
        message: str = "Некорректный синтаксис или запрос",
    ):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=message)


class NotFoundException(CustomHTTPException):
    def __init__(self, message: str = "Не найдено"):
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=message)


class ForbiddenException(CustomHTTPException):
    def __init__(
        self,
        message: str = "Запрос запрещён - авторизация не поможет",
    ):
        super().__init__(status_code=HTTPStatus.FORBIDDEN, detail=message)


class UnauthorizedException(CustomHTTPException):
    def __init__(self, message: str = "Нет прав, авторизуйтесь"):
        super().__init__(status_code=HTTPStatus.UNAUTHORIZED, detail=message)


class UnprocessableEntityException(CustomHTTPException):
    def __init__(self, message: str = "Необрабатываемая сущность"):
        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=message,
        )


class DuplicateValueException(CustomHTTPException):
    def __init__(
        self,
        message: str = "Ошибка дубликата, такая сущность уже существует",
    ):
        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=message,
        )
