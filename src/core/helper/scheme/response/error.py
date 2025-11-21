"""Error response."""
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response."""

    error_code: int = Field(..., examples=[401,500])
    detail: str = Field(..., examples=["Не авторизирован", "Ошибка сервера"])
