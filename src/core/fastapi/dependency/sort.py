"""Sort Dependency."""

from src.core.helper.type.sort import SortParams, SortType


def get_sort_params(
    sort_by: str | None = None,
    sort_type: SortType = SortType.asc,
) -> SortParams:
    """Depends for sorting."""
    return SortParams(sort_by=sort_by, sort_type=sort_type)
