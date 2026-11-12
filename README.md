# fastapi-template

[![CI](https://github.com/begenFys/fastapi-template/actions/workflows/ci.yaml/badge.svg)](https://github.com/begenFys/fastapi-template/actions/workflows/ci.yaml)

A starting point for async FastAPI services on PostgreSQL. It gives a new
service a layered structure, JWT authentication, migrations, tests and a
Docker setup from the first commit, so work starts with the domain rather
than the plumbing.

## What's inside

- **Layers.** Router → controller → repository, wired by a factory through
  FastAPI dependencies. The generic SQLAlchemy repository and controller
  already handle filtering, sorting, pagination, projections and
  transactions; a new entity mostly needs a model and two short classes.
- **Authentication.** Register, login, refresh and logout under
  `/api/v1/auth`, current user at `/api/v1/user/me`. Short-lived access JWTs
  and single-use refresh tokens that rotate on every refresh; presenting a
  used refresh token revokes all of the user's sessions. Passwords are hashed
  with Argon2.
- **Database.** SQLAlchemy 2.0 async with asyncpg, Alembic migrations, a
  session per request with commit or rollback at the end.
- **Errors and logs.** Common exceptions map to JSON error responses
  (conflicts, including database unique violations, become `409`); requests are logged with loguru.
- **Running.** Uvicorn with reload in development, Gunicorn with Uvicorn
  workers otherwise. Swagger UI at `/api/docs`, disabled in production.
- **Quality.** Ruff, mypy in strict mode, pytest with testcontainers,
  pre-commit hooks and a GitHub Actions workflow.

## Quick start

Requires [uv](https://docs.astral.sh/uv/) and Docker.

```bash
cp .env.test.example .env.test
cp .env.dev.example .env.dev
make sync
make docker-setup-test
make dc-up-db-test
make migrate
make start
```

The database runs in Docker on port 3454, the app runs locally on
http://127.0.0.1:8000. Open http://127.0.0.1:8000/api/docs, call
`POST /api/v1/auth/register`, then use the **Authorize** button with the
same username and password.

Without Swagger:

```bash
curl -X POST localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "jane", "email": "jane@example.com", "password": "correct-horse-battery"}'

curl -X POST localhost:8000/api/v1/auth/login \
  -d "username=jane&password=correct-horse-battery"
# {"access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 900}

curl localhost:8000/api/v1/user/me -H "Authorization: Bearer <access_token>"
```

To run the whole stack in Docker instead (app image built locally, port
8101):

```bash
make dc-start-test
```

## Starting a new service from it

1. Create a repository from this one and rename the project in
   `pyproject.toml` and `Makefile` (`PROJECT_NAME`, `DOCKER_USERNAME`); a
   pre-commit hook checks that they match.
2. Set a real `SECRET_KEY` in every `.env.*` file: `openssl rand -hex 32`.
3. Add an entity the same way `User` is built:
   - model in `src/app/model/`,
   - migration: `make generate-migration`, then review the generated file,
   - repository in `src/app/repository/` (usually just a subclass),
   - controller in `src/app/controller/`,
   - a `get_..._controller` method in `src/app/factory/factory.py`,
   - router in `src/api/v1/`, included in `src/api/v1/__init__.py`.
4. Protect an endpoint by adding a `user: CurrentUser` parameter
   (`src/app/dependency`).

## Tests and checks

```bash
make test      # pytest; PostgreSQL is started by testcontainers
make lint      # ruff
make format    # ruff format + autofix
make check-types
```

The test database is built by running the migrations, so the tests also
check that migrations apply. To use an existing database instead of a
container, set the `POSTGRES_*` variables before running pytest.

## Configuration

Settings are read from environment variables (`src/core/setting.py`); the
Makefile loads them from `.env.dev`, Docker Compose from `.env.test` or
`.env.prod`.

| Variable | Meaning |
|---|---|
| `ENVIRONMENT` | `dev`, `test` or `prod`; `prod` hides the API docs |
| `PORT`, `WORKERS_COUNT` | server port and Gunicorn workers |
| `SECRET_KEY` | JWT signing key, at least 32 characters |
| `ACCESS_TOKEN_TTL_MINUTES` | access token lifetime, default 15 |
| `REFRESH_TOKEN_TTL_DAYS` | refresh token lifetime, default 30 |
| `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | database connection |

## Deployment

`make docker-buildx-and-push-prod` builds and pushes a multi-platform image.
The `CD` workflow (manual run) copies the configs to a server over SSH and
restarts the stack with `make dc-start-prod`; it expects the server and
database settings in the repository's Actions variables and secrets.

## Project layout

```
src/
  api/            routers: extra/ (health), v1/ (auth, user)
  app/            this service: models, repositories, controllers,
                  schemes, factory, dependencies
  core/           reusable base: generic repository and controller,
                  database session, security, error handlers, logging
  migration/      Alembic environment and versions
tests/            API and security tests
```
