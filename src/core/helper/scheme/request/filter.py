"""Filter request."""

from typing import Any

from pydantic import BaseModel, Field

from src.core.helper.type.filter import FilterType, OperatorType


class FilterParam(BaseModel):
    """Filter parameter."""

    field: str = Field(..., examples=["message"])
    value: Any = Field(..., examples=["abc"])
    operator: OperatorType = Field(..., examples=[OperatorType.EQUALS])


class FilterRequest(BaseModel):
    """Filter request."""

    filters: list[FilterParam] = Field([])
    type: FilterType = Field(FilterType.AND)

    def __repr__(self) -> str:
        """Представление данных схемы для ключа."""
        filters_repr = (
            "; ".join(f"{filter_param}" for filter_param in self.filters)
            if self.filters
            else "None"
        )
        return f"{self.__class__.__name__}(filters=[{filters_repr}], type={self.type})"
