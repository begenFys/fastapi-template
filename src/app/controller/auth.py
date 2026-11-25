"""Registration, login and token refresh."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select

from src.app.model import RefreshToken, User
from src.app.repository import RefreshTokenRepository, UserRepository
from src.app.scheme.request.auth import RegisterRequest
from src.app.scheme.response.token import TokenResponse
from src.core.exception.base import (
    ConflictException,
    UnauthorizedException,
)
from src.core.security import (
    TokenType,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.core.setting import settings


class AuthController:
    """Registration, login and token refresh.

    Access tokens are stateless. Refresh tokens are stored by `jti`, are
    single-use and rotate on every refresh. Presenting an already used
    refresh token revokes all of the user's sessions, since it means the
    token was copied.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.session = user_repository.session

    async def register(self, data: RegisterRequest) -> User:
        """Create a user.

        Raises:
            ConflictException: Username or email is taken.
        """
        email = data.email.lower()
        taken = await self.session.scalar(
            select(User.id).where(
                or_(User.username == data.username, User.email == email),
            ),
        )
        if taken is not None:
            raise ConflictException("Username or email is already taken")

        user = User(
            username=data.username,
            email=email,
            hashed_password=hash_password(data.password),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def login(self, login: str, password: str) -> TokenResponse:
        """Check credentials and issue a token pair.

        Args:
            login: Username or email.
            password: Plain password.

        Raises:
            UnauthorizedException: Wrong login or password.
        """
        user = await self.session.scalar(
            select(User).where(
                or_(User.username == login, User.email == login.lower()),
            ),
        )
        hashed = user.hashed_password if user else None
        if not verify_password(password, hashed) or user is None:
            raise UnauthorizedException("Incorrect login or password")
        return await self._issue_tokens(user.id)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Exchange a refresh token for a new pair.

        Raises:
            UnauthorizedException: Token is invalid, expired or already used.
        """
        payload = decode_token(refresh_token, TokenType.refresh)
        user_id = await self.refresh_token_repository.consume(payload.jti)
        if user_id is None:
            # Valid signature but not consumable: expired, unknown or reused.
            # Reuse means the token leaked, so end every session of the user.
            await self.refresh_token_repository.revoke_all(payload.sub)
            await self.session.commit()
            raise UnauthorizedException("Refresh token is no longer valid")
        return await self._issue_tokens(user_id)

    async def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token. Unknown or used tokens are ignored."""
        payload = decode_token(refresh_token, TokenType.refresh)
        await self.refresh_token_repository.consume(payload.jti)
        await self.session.commit()

    async def get_current_user(self, access_token: str) -> User:
        """Resolve the user from an access token.

        Raises:
            UnauthorizedException: Token is invalid or the user is gone.
        """
        payload = decode_token(access_token, TokenType.access)
        user = await self.session.get(User, payload.sub)
        if user is None:
            raise UnauthorizedException("User not found")
        return user

    async def _issue_tokens(self, user_id: uuid.UUID) -> TokenResponse:
        access_ttl = timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES)
        refresh_ttl = timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)
        access_token, _ = create_token(user_id, TokenType.access, access_ttl)
        refresh_token, refresh_payload = create_token(
            user_id,
            TokenType.refresh,
            refresh_ttl,
        )
        self.session.add(
            RefreshToken(
                id=refresh_payload.jti,
                user_id=user_id,
                expires_at=datetime.fromtimestamp(refresh_payload.exp, UTC),
            ),
        )
        await self.session.commit()
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_ttl.total_seconds()),
        )
