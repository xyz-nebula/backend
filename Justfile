run-dev:
    uv run app

run-docker:
    docker compose -f docker-compose.dev.yml up

build-docker:
    docker build -t nebula-backend .
