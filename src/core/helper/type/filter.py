"""Types for filters."""

from enum import StrEnum


class FilterType(StrEnum):
    """Filter types."""

    AND = "AND"
    OR = "OR"


class OperatorType(StrEnum):
    """Operator types."""

    EQUALS = "EQUALS"
    NOT_EQUAL = "NOT_EQUAL"
    IN = "IN"
    NOT_IN = "NOT_IN"
    GREATER = "GREATER"
    EQUALS_OR_GREATER = "EQUALS_OR_GREATER"
    LESS = "LESS"
    EQUALS_OR_LESS = "EQUALS_OR_LESS"
    STARTS_WITH = "STARTS_WITH"
    NOT_START_WITH = "NOT_START_WITH"
    ENDS_WITH = "ENDS_WITH"
    NOT_END_WITH = "NOT_END_WITH"
    CONTAINS = "CONTAINS"
    NOT_CONTAIN = "NOT_CONTAIN"
    ELEM_MATCH = "ELEM_MATCH"
