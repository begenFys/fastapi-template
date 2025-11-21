"""Types for controller logic."""

from enum import StrEnum


class DTOMode(StrEnum):
    """DTO Mode."""

    pydantic = "pydantic"
    dict = "dict"
