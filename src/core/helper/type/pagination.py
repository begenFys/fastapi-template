"""Types for pagination."""

from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = 0
    limit: int = 100
