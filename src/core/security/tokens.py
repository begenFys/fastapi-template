"""JWT access and refresh tokens."""

import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum

import jwt
from pydantic import BaseModel, ValidationError

from src.core.exception.base import UnauthorizedException
from src.core.setting import settings


class TokenType(StrEnum):
    """Token type, stored in the `type` claim."""

    access = "access"
    refresh = "refresh"


class TokenPayload(BaseModel):
    """Validated token claims."""

    sub: uuid.UUID
    jti: uuid.UUID
    type: TokenType
    iat: int
    exp: int


def create_token(
    subject: uuid.UUID,
    token_type: TokenType,
    ttl: timedelta,
    jti: uuid.UUID | None = None,
) -> tuple[str, TokenPayload]:
    """Create a signed token.

    Args:
        subject: User id, stored in `sub`.
        token_type: Access or refresh.
        ttl: Token lifetime.
        jti: Token id. Generated if not given.

    Returns:
        Encoded token and its claims.
    """
    now = datetime.now(UTC)
    payload = TokenPayload(
        sub=subject,
        jti=jti or uuid.uuid4(),
        type=token_type,
        iat=int(now.timestamp()),
        exp=int((now + ttl).timestamp()),
    )
    token = jwt.encode(
        payload.model_dump(mode="json"),
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, payload


def decode_token(token: str, expected_type: TokenType) -> TokenPayload:
    """Verify a token and return its claims.

    Args:
        token: Encoded token.
        expected_type: Token type the caller accepts.

    Returns:
        Token claims.

    Raises:
        UnauthorizedException: Token is invalid, expired or of another type.
    """
    try:
        raw = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["sub", "jti", "type", "iat", "exp"]},
        )
        payload = TokenPayload.model_validate(raw)
    except (jwt.PyJWTError, ValidationError) as exc:
        raise UnauthorizedException("Invalid or expired token") from exc
    if payload.type != expected_type:
        raise UnauthorizedException("Invalid token type")
    return payload
