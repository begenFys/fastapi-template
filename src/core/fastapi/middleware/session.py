"""SessionMiddleware(PostgresSession)."""

from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

from src.core.database.session import (
    reset_session_context,
    set_session_context,
)


class SessionMiddleware:
    """Session middleware."""

    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Set session context."""
        session_id = str(uuid4())
        context = set_session_context(session_id=session_id)

        try:
            await self.app(scope, receive, send)
        finally:
            reset_session_context(context=context)
