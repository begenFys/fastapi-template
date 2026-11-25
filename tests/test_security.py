"""Password hashing and token helpers."""

import uuid
from datetime import timedelta

import pytest
from src.core.exception.base import UnauthorizedException
from src.core.security import (
    TokenType,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_round_trip() -> None:
    hashed = hash_password("correct-horse")

    assert hashed != "correct-horse"
    assert verify_password("correct-horse", hashed)
    assert not verify_password("wrong-horse", hashed)


def test_missing_user_never_verifies() -> None:
    assert not verify_password("anything", None)


def test_token_round_trip() -> None:
    user_id = uuid.uuid4()
    token, payload = create_token(
        user_id,
        TokenType.access,
        timedelta(minutes=5),
    )

    decoded = decode_token(token, TokenType.access)

    assert decoded.sub == user_id
    assert decoded.jti == payload.jti


def test_token_type_is_checked() -> None:
    token, _ = create_token(uuid.uuid4(), TokenType.refresh, timedelta(days=1))

    with pytest.raises(UnauthorizedException):
        decode_token(token, TokenType.access)


def test_expired_token_is_rejected() -> None:
    token, _ = create_token(
        uuid.uuid4(),
        TokenType.access,
        timedelta(seconds=-1),
    )

    with pytest.raises(UnauthorizedException):
        decode_token(token, TokenType.access)


def test_tampered_token_is_rejected() -> None:
    token, _ = create_token(
        uuid.uuid4(),
        TokenType.access,
        timedelta(minutes=5),
    )
    header, payload, signature = token.split(".")
    tampered = f"{header}.{payload}.{signature[::-1]}"

    with pytest.raises(UnauthorizedException):
        decode_token(tampered, TokenType.access)
