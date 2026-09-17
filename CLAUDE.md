# nebula-backend

FastAPI backend for the Nebula project. Python 3.14+, managed with `uv`.

## Stack

- **FastAPI** + **Uvicorn** — web framework
- **Tortoise ORM** + **Postgres** — async database ORM (`User` model implemented; see `app/database/models.py`)
- **PyJWT** — JWT auth (access tokens only — refresh tokens are opaque, stored in Valkey)
- **Valkey** (Redis-compatible) — token/session storage: activation codes and refresh tokens, both TTL-based
- **aiosmtplib** — activation email delivery (prod); logs the link instead in dev (`MAILER_TYPE`)
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
# Docker dev stack (app + valkey + postgres)
just run-dev

# Reset the dev Postgres database (drops the postgres container + volume)
just reset-db

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
├── api/v1/routers/     # Route handlers — auth.py implements the openapi.yaml auth API
├── config/             # Pydantic Settings, StorageTypes/MailerType enums, ValkeyConfig
├── database/           # User model (Tortoise) + query/mutation helpers in actions.py
├── dependencies.py     # FastAPI Depends() for Bearer token extraction
├── exceptions.py        # ApiException + handlers -> {code, message, field} error envelope
├── middleware/         # JWTAuthenticationMiddleware (see note below)
├── repository/         # BaseRepository, LocalRepository, ValkeyRepository, RepositoryFactory
├── services/           # JWTService (encode/decode), AuthService (register/activate/login/
│                        # refresh/logout), mailer.py (ActivationMailer: SMTP prod / log dev)
└── utils/              # time_helpers (cast_to_seconds), password (bcrypt hash/verify)
```

## Auth flow

Implements `openapi.yaml` (register → email activation → login → refresh → logout).
See `app/services/AuthService.py` for the full flow. Key points:
- Access tokens are short-lived JWTs (`JWTService`, HS256, never revoked server-side).
  Refresh tokens are opaque (`secrets.token_urlsafe`), stored in Valkey as
  `refresh:{token} -> user_uuid` with a TTL, and rotated (old one deleted) on every use.
- Activation codes are opaque UUIDs stored in Valkey as `activation:{code} -> user_uuid`
  with a TTL — there's no separate Postgres table for them or for refresh tokens, since
  Valkey already covers ephemeral, TTL-based storage.
- `dependencies.py` provides `get_current_token_payload()` as a FastAPI `Depends()`,
  used to protect `logout` (the only endpoint in this API that requires a bearer token).
- **Note:** `JWTAuthenticationMiddleware` is still unwired and has no path-exclusion
  support — the auth router relies on `get_current_token_payload()` per-route instead.
- MFA/TOTP: `User.mfa_enabled`/`mfa_secret` exist and `login` checks them, but there's no
  enrollment endpoint yet, so `mfa_enabled` is always `False` in practice.
- Rate limiting (429s in the spec) is not implemented yet.

## Storage backends

Controlled by `StorageTypes` enum in `app/config/storage_type.py`:

| Value | Class | Use case |
|---|---|---|
| `valkey` | `ValkeyRepository` | Production / distributed |
| `memory` | `LocalRepository` | Local dev / testing |

Use `RepositoryFactory.create(config)` to get the right backend.
