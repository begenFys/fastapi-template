"""Pagination response"""
from pydantic import BaseModel, ConfigDict, Field


class PaginationResponse[T](BaseModel):
    """Pagination response."""
    page: int = Field(..., examples=[0])
    page_size: int = Field(..., examples=[0])
    total_pages: int = Field(..., examples=[0])
    total_count: int = Field(..., examples=[0])
    data: list[T] = Field(...)

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )
