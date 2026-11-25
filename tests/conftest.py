"""Test setup.

Settings and the database engine are created when `src` is imported, so the
environment is prepared here, before any test module imports the app. If
POSTGRES_HOST is not set, PostgreSQL is started with testcontainers.
"""

import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from testcontainers.community.postgres import PostgresContainer

ROOT = Path(__file__).resolve().parent.parent

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-1234")

_container: PostgresContainer | None = None
if "POSTGRES_HOST" not in os.environ:
    _container = PostgresContainer("postgres:16", driver="asyncpg")
    _container.start()
    os.environ.update(
        POSTGRES_HOST=_container.get_container_host_ip(),
        POSTGRES_PORT=str(_container.get_exposed_port(5432)),
        POSTGRES_DB=_container.dbname,
        POSTGRES_USER=_container.username,
        POSTGRES_PASSWORD=_container.password,
    )


def pytest_unconfigure(config: pytest.Config) -> None:
    """Stop the container started for the test run."""
    if _container is not None:
        _container.stop()


from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from src.core.database.session import engines  # noqa: E402
from src.core.fastapi.application import get_app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _migrate() -> Iterator[None]:
    """Build the schema with migrations, so every run checks them too."""
    config = Config(str(ROOT / "alembic.ini"))
    command.upgrade(config, "head")
    yield
    command.downgrade(config, "base")


@pytest.fixture(scope="session")
async def app() -> AsyncIterator[FastAPI]:
    """Application with its lifespan running (routers are added there)."""
    application = get_app()
    async with application.router.lifespan_context(application):
        yield application
    for engine in engines.values():
        await engine.dispose()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """HTTP client bound to the app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
async def _clean_tables(app: FastAPI) -> AsyncIterator[None]:
    yield
    async with engines["writer"].begin() as conn:
        await conn.execute(text('TRUNCATE TABLE "user" CASCADE'))
