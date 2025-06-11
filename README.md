# Castera Backend

This repository contains the backend for the **Castera** application. It is built with Django and exposes REST APIs alongside WebSocket support through Django Channels.

## Requirements

- Docker and Docker Compose (recommended)
- Alternatively, Python 3.11+ with PostgreSQL and Redis

## Running with Docker

Build the containers and start the services:

```bash
docker compose up --build
```

The web service listens on port `8100` by default. A PostgreSQL database and a Redis instance are started automatically.

Apply database migrations with:

```bash
docker compose run web python manage.py migrate
```

## Running Tests

Ensure the PostgreSQL and Redis services are running (e.g. with `docker compose up -d`).
Then execute the project tests using the Django test runner and the test settings module:

```bash
docker compose run web python manage.py test --settings=config.test_settings
```

## Project Structure

- `config/` – Django project configuration
- `users/` – user management app
- `meetings/` – meeting and signaling logic

Feel free to adapt the configuration files to your environment.
