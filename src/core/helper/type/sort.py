"""Types for sorting."""

from enum import StrEnum

from pydantic import BaseModel, Field


class SortType(StrEnum):
    """Sort types."""

    asc = "asc"
    desc = "desc"


class SortParams(BaseModel):
    """Sorting parameters."""

    sort_by: str | None = Field(None, examples=["id"])
    sort_type: SortType = Field(SortType.asc, examples=["asc", "desc"])
