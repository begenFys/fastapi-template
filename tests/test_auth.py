"""Auth API: register, login, me, refresh, logout."""

from http import HTTPStatus
from typing import Any

import pytest
from httpx import AsyncClient

USER = {
    "username": "jane",
    "email": "Jane@Example.com",
    "password": "correct-horse-battery",
}


async def register(client: AsyncClient) -> dict[str, Any]:
    response = await client.post("/api/v1/auth/register", json=USER)
    assert response.status_code == HTTPStatus.CREATED, response.text
    return response.json()


async def login(client: AsyncClient, login: str = "jane") -> dict[str, Any]:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": login, "password": USER["password"]},
    )
    assert response.status_code == HTTPStatus.OK, response.text
    return response.json()


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_register_hides_password(client: AsyncClient) -> None:
    user = await register(client)

    assert user["username"] == "jane"
    assert user["email"] == "jane@example.com"
    assert "password" not in user
    assert "hashed_password" not in user


@pytest.mark.parametrize(
    "duplicate",
    [
        {"email": "other@example.com"},
        {"username": "other", "email": "JANE@example.com"},
    ],
)
async def test_register_duplicate(
    client: AsyncClient,
    duplicate: dict[str, str],
) -> None:
    await register(client)

    response = await client.post(
        "/api/v1/auth/register",
        json=USER | duplicate,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("login_value", ["jane", "jane@example.com"])
async def test_login_and_me(client: AsyncClient, login_value: str) -> None:
    await register(client)
    tokens = await login(client, login_value)

    response = await client.get(
        "/api/v1/user/me",
        headers=bearer(tokens["access_token"]),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["username"] == "jane"
    assert tokens["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient) -> None:
    await register(client)

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "jane", "password": "wrong-password"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_me_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/user/me")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_refresh_token_is_not_an_access_token(
    client: AsyncClient,
) -> None:
    await register(client)
    tokens = await login(client)

    response = await client.get(
        "/api/v1/user/me",
        headers=bearer(tokens["refresh_token"]),
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_refresh_rotates_token(client: AsyncClient) -> None:
    await register(client)
    tokens = await login(client)

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == HTTPStatus.OK
    new_tokens = response.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]
    me = await client.get(
        "/api/v1/user/me",
        headers=bearer(new_tokens["access_token"]),
    )
    assert me.status_code == HTTPStatus.OK


async def test_reused_refresh_token_revokes_all_sessions(
    client: AsyncClient,
) -> None:
    await register(client)
    first = await login(client)
    other_device = await login(client)
    rotated = (
        await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": first["refresh_token"]},
        )
    ).json()

    reuse = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first["refresh_token"]},
    )

    assert reuse.status_code == HTTPStatus.UNAUTHORIZED
    for tokens in (rotated, other_device):
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_logout_revokes_refresh_token(client: AsyncClient) -> None:
    await register(client)
    tokens = await login(client)

    logout = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
    )
    refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert logout.status_code == HTTPStatus.NO_CONTENT
    assert refresh.status_code == HTTPStatus.UNAUTHORIZED


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/api/health")

    assert response.status_code == HTTPStatus.OK
