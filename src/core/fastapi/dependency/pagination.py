"""Pagination Dependency."""

from src.core.helper.type.pagination import PaginationParams


def get_pagination_params(
    skip: int = 0,
    limit: int = 100,
) -> PaginationParams:
    """Depends for pagination."""
    return PaginationParams(skip=skip, limit=limit)
