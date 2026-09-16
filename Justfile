run-dev: 
    uv run app

build-docker:
    docker build -t nebula-backend .

run-docker: build-docker
    docker compose -f docker-compose.dev.yml up
