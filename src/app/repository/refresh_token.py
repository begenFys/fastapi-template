"""Refresh token repository."""

import uuid

from sqlalchemy import Select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.model import RefreshToken
from src.core.repository import SQLAlchemyRepository


class RefreshTokenRepository(
    SQLAlchemyRepository[RefreshToken, AsyncSession, Select],  # type: ignore[type-arg]
):
    """Refresh token repository."""

    async def consume(self, token_id: uuid.UUID) -> uuid.UUID | None:
        """Revoke a valid token in one statement.

        Only one of several concurrent requests with the same token gets
        a row back, so a refresh token can be exchanged exactly once.

        Args:
            token_id: Token `jti`.

        Returns:
            Owner's user id, or None if the token is unknown, expired or
            already revoked.
        """
        result = await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.id == token_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > func.now(),
            )
            .values(revoked_at=func.now())
            .returning(RefreshToken.user_id),
        )
        return result.scalar_one_or_none()

    async def revoke_all(self, user_id: uuid.UUID) -> None:
        """Revoke every active refresh token of a user."""
        await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=func.now()),
        )
