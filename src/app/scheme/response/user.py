"""User response."""

import uuid

from pydantic import ConfigDict, Field

from src.core.helper.scheme.response.timestamp import (
    BaseModelWithTimestamp,
)


class UserResponse(BaseModelWithTimestamp):
    """User response."""

    id: uuid.UUID
    username: str = Field(..., examples=["jane"])
    email: str = Field(..., examples=["jane@example.com"])

    model_config = ConfigDict(from_attributes=True)
