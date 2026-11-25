"""Auth requests."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """New user."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=255,
        pattern=r"^[A-Za-z0-9_.-]+$",
        examples=["jane"],
    )
    email: EmailStr = Field(..., examples=["jane@example.com"])
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["correct-horse-battery"],
    )


class RefreshRequest(BaseModel):
    """Refresh token to exchange or revoke."""

    refresh_token: str
