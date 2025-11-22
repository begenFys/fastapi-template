"""Count response."""

from pydantic import BaseModel, Field


class CountResponse(BaseModel):
    """Count response."""

    count: int = Field(..., examples=[100])
