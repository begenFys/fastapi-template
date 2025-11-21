"""Base model with timestamp"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseModelWithTimestamp(BaseModel):
    """Base model with timestamp."""

    created_at: datetime = Field(
        ...,
        examples=[datetime.now()],
        description="ISO-8601 timestamp",
    )
    updated_at: datetime = Field(
        ...,
        examples=[datetime.now()],
        description="ISO-8601 timestamp",
    )

    model_config = ConfigDict(
        from_attributes=True,
    )
