"""Session dependency."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session


class PostgresSession:
    """FastAPI Depends for getting session Postgres(SQLAlchemy)."""

    def __init__(
        self,
        db_session: AsyncSession | async_scoped_session[AsyncSession],
    ):
        self.db_session = db_session

    async def __call__(
        self,
    ) -> AsyncGenerator[
        AsyncSession | async_scoped_session[AsyncSession],
        None,
    ]:
        """Get session Postgres(SQLAlchemy).

        Yields:
            Session database.
        """
        try:
            yield self.db_session
        except Exception:
            await self.db_session.rollback()
            raise
        finally:
            await self.db_session.commit()
            if isinstance(self.db_session, async_scoped_session):
                # Drop the request's session from the registry, otherwise
                # every request leaves an entry behind.
                await self.db_session.remove()
            else:
                await self.db_session.close()
