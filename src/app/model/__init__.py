"""Service models."""

import pkgutil
from pathlib import Path

from .refresh_token import RefreshToken
from .user import User


def load_all_models() -> None:
    """Загружаем все модели из этой папки."""
    package_dir = Path(__file__).resolve().parent
    modules = pkgutil.walk_packages(
        path=[str(package_dir)],
        prefix="src.app.model.",
    )
    for module in modules:
        __import__(module.name)


__all__ = [
    "load_all_models",
    "RefreshToken",
    "User",
]
