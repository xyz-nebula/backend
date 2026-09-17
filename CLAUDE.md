# nebula-backend

FastAPI backend for the Nebula project. Python 3.14+, managed with `uv`.

## Stack

- **FastAPI** + **Uvicorn** — web framework
- **Tortoise ORM** — async database ORM (models not yet implemented)
- **PyJWT** — JWT auth
- **Valkey** (Redis-compatible) — token/session storage
- **Pydantic Settings** — config from `.env`

## Setup

1. Copy `.env.example` to `.env` and fill in values:
   ```
   JWT_SECRET_KEY=your-secret
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_MINUTES=60
   VALKEY_HOST=localhost
   VALKEY_PORT=6379
   VALKEY_DB=0
   ```

2. Install dependencies:
   ```
   uv sync
   ```

## Running

```bash
# Local dev (no Docker)
just run-dev
# or directly:
uv run app

# Docker dev build + run
just run-docker

# Docker production build only
just build-docker
```

## Valkey (local dev)

Spin up a local Valkey instance with Docker:

```bash
docker run -d --name valkey -p 6379:6379 \
  --health-cmd="valkey-cli ping" \
  --health-interval=5s \
  valkey/valkey:8
```

Stop and remove when done:

```bash
docker stop valkey && docker rm valkey
```

## Project structure

```
app/
├── api/v1/routers/     # Route handlers (auth.py is a placeholder)
├── config/             # Pydantic Settings, StorageTypes enum, ValkeyConfig
├── database/           # Tortoise ORM models and actions (not yet implemented)
├── dependencies.py     # FastAPI Depends() for Bearer token extraction
├── middleware/         # JWTAuthenticationMiddleware
├── repository/         # BaseRepository, LocalRepository, ValkeyRepository, RepositoryFactory
├── services/           # JWTService (decode/validate tokens)
└── utils/              # time_helpers (cast_to_seconds)
```

## Auth flow

- `JWTAuthenticationMiddleware` extracts the Bearer token from the `Authorization` header,
  validates it via `JWTService`, and stores the decoded payload in `scope["state"]["user"]`.
- `dependencies.py` provides `get_current_token_payload()` as a FastAPI `Depends()` for
  protecting individual routes.
- **Note:** the middleware currently has no excluded paths — public routes (login, register)
  must be added to a bypass list before the middleware is wired up.

## Commit conventions

Prefer small, focused commits over one large commit bundling unrelated changes —
split a change into a chain of commits along natural seams (e.g. dependency/config
setup, then infra, then each logical unit) rather than committing everything at once.
Format: `feat: <feature-name>: <msg>` (also `fix:`, `refactor:`, `test:`, `docs:`
as appropriate in place of `feat:`).

## Storage backends

Controlled by `StorageTypes` enum in `app/config/storage_type.py`:

| Value | Class | Use case |
|---|---|---|
| `valkey` | `ValkeyRepository` | Production / distributed |
| `memory` | `LocalRepository` | Local dev / testing |

Use `RepositoryFactory.create(config)` to get the right backend.
