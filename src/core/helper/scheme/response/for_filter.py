"""For filters response"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ForFiltersResponse(BaseModel):
    """For filters response."""

    columns: dict[str, list[Any] | dict[str, Any]] = Field(...)

    model_config = ConfigDict(from_attributes=True)
