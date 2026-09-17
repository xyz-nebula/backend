run-dev:
    docker compose -f docker-compose.dev.yml up

build-docker:
    docker build -t nebula-backend .

reset-db:
    docker compose -f docker-compose.dev.yml rm -sf postgres
    docker volume rm $(docker volume ls -q --filter label=com.docker.compose.volume=postgres_data)
