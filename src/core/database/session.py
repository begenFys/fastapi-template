"""Session for database."""

from contextvars import ContextVar, Token
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Delete, Insert, Update

from src.core.setting import settings

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    """Get session context."""
    return session_context.get()


def set_session_context(session_id: str) -> Token[str]:
    """Set session context."""
    return session_context.set(session_id)


def reset_session_context(context: Token[str]) -> None:
    """Reset session context."""
    session_context.reset(context)


class RoutingSession(Session):
    """Routing session."""

    def __init__(
        self,
        engines: dict[str, AsyncEngine],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.engines = engines

    def get_bind(  # type: ignore[no-untyped-def]
        self,
        mapper=None,
        clause=None,
        **kw,
    ):
        """Get bind."""
        if self._flushing or isinstance(clause, (Update, Delete, Insert)):
            return self.engines["writer"].sync_engine
        return self.engines["reader"].sync_engine


engines = {
    "writer": create_async_engine(
        str(settings.POSTGRES_URL),
        pool_recycle=3600,
    ),
    "reader": create_async_engine(
        str(settings.POSTGRES_URL),
        pool_recycle=3600,
    ),
}


async_session_factory = async_sessionmaker(
    class_=AsyncSession,
    sync_session_class=RoutingSession,
    expire_on_commit=False,
    engines=engines,
)

db_session: AsyncSession | async_scoped_session[AsyncSession] = (
    async_scoped_session(
        session_factory=async_session_factory,
        scopefunc=get_session_context,
    )
)
