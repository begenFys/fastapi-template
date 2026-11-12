"""Token response."""

from typing import Literal

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105
    expires_in: int = Field(..., description="Access token lifetime, seconds")
