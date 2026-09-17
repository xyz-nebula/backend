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
├── dependencies.py     # get_current_token_payload() — sole bearer-token verifier
├── exceptions.py        # ApiException + handlers -> {code, message, field} error envelope
├── repository/         # BaseRepository, LocalRepository, ValkeyRepository, RepositoryFactory
├── services/           # JWTService (encode/decode), AuthService (register/activate/login/
│                        # refresh/logout/totp enroll-confirm-disable), mailer.py
│                        # (ActivationMailer: SMTP prod / log dev)
└── utils/              # time_helpers (cast_to_seconds), password (bcrypt hash/verify)
```

## Auth flow

Implements `openapi.yaml` (register → email activation → login → refresh → logout,
plus TOTP/MFA enrollment). See `app/services/AuthService.py` for the full flow. Key
points:
- Access tokens are short-lived JWTs (`JWTService`, HS256, never revoked server-side).
  Refresh tokens are opaque (`secrets.token_urlsafe`), stored in Valkey as
  `refresh:{token} -> user_uuid` with a TTL, and rotated (old one deleted) on every use.
- Activation codes are opaque UUIDs stored in Valkey as `activation:{code} -> user_uuid`
  with a TTL — there's no separate Postgres table for them or for refresh tokens, since
  Valkey already covers ephemeral, TTL-based storage.
- `app/api/v1/routers/auth.py` splits its routes into `public_router` (register,
  activate, login, refresh — no auth) and `protected_router` (logout, `totp/*`), the
  latter with `dependencies=[Depends(get_current_token_payload)]` at the router level
  — every route added to it requires a bearer token without repeating the `Depends`.
  There's no ASGI auth middleware; `get_current_token_payload`
  (`app/dependencies.py`) is the *only* place a bearer token is verified.
- TOTP/MFA: `POST /v1/auth/totp/enroll` generates a secret (stored on `User.mfa_secret`,
  `mfa_enabled` stays `False`), `POST /v1/auth/totp/confirm` verifies a code against it
  and flips `mfa_enabled` on, `DELETE /v1/auth/totp` (password-confirmed) turns it back
  off. `login` then requires `totp_token` whenever `mfa_enabled` is `True`.
- Rate limiting (429s in the spec) is not implemented yet.

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
