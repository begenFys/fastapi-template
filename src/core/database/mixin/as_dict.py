"""As dict mixin."""

from typing import Any


class AsDictMixin:
    """As dict mixin."""

    def as_dict(self) -> dict[str, Any]:
        """Return dict representation of object."""
        return self.__dict__
