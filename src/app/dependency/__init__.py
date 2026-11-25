"""FastAPI dependencies."""

from .auth import CurrentUser, get_current_user, oauth2_scheme

__all__ = ("CurrentUser", "get_current_user", "oauth2_scheme")
