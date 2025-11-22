"""User response."""

from pydantic import ConfigDict, Field

from src.core.helper.scheme.response.timestamp import (
    BaseModelWithTimestamp,
)


class UserResponse(BaseModelWithTimestamp):
    """User response."""

    id: str = Field(..., examples=["1"])
    username: str = Field(..., examples=["Марлон Марлонов"])
    email: str = Field(..., examples=["marlon@marlerino.group"])

    model_config = ConfigDict(from_attributes=True)
