run-dev:
    docker compose -f docker-compose.dev.yml up --build --remove-orphans

build-docker:
    docker build -t nebula-backend .

reset-db:
    docker compose -f docker-compose.dev.yml rm -sf postgres
    docker volume rm $(docker volume ls -q --filter label=com.docker.compose.volume=postgres_data)

db-migrate name="update": sync
    uv run aerich migrate --name {{name}}

db-upgrade: sync
    uv run aerich upgrade

db-downgrade: sync
    uv run aerich downgrade

sync:
    uv sync --dev

lint: sync
    uv run ruff check .

lint-fix: sync
    uv run ruff check --fix .

fmt: sync
    uv run ruff format .

fmt-check: sync
    uv run ruff format --check .

typecheck: sync
    uv run ty check

test: sync
    uv run --dev pytest -q

check: lint fmt-check typecheck test
