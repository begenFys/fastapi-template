"""Projection Dependency."""


def get_projection(
    projection: str | None = None,
) -> list[str] | None:
    """Depends for projection."""
    if projection:
        return projection.split(",")
    return None
