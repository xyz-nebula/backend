run-dev:
    docker compose -f docker-compose.dev.yml up

build-docker:
    docker build -t nebula-backend .

reset-db:
    docker compose -f docker-compose.dev.yml rm -sf postgres
    docker volume rm $(docker volume ls -q --filter label=com.docker.compose.volume=postgres_data)

sync:
    uv sync --dev

lint: sync
    uv run ruff check .

fmt: sync
    uv run ruff format .

fmt-check: sync
    uv run ruff format --check .

typecheck: sync
    uv run pyright

test: sync
    uv run --dev pytest -q

check: lint fmt-check typecheck test
