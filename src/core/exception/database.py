"""Кастомные ошибки для database."""

from http import HTTPStatus

from src.core.exception.base import CustomHTTPException


class FieldException(CustomHTTPException):
    """Field Exception."""

    def __init__(self, message: str = "Недопустимое поле."):
        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=message,
        )
