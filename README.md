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

To access the Django admin you will need a superuser account:

```bash
docker compose run web python manage.py createsuperuser
```

Once created, visit `http://localhost:8100/admin/` and log in with the credentials.

Apply database migrations with:

```bash
docker compose run web python manage.py migrate
```

### Running Daphne Locally

For local development with WebSockets you can launch the ASGI server using
[`daphne`](https://github.com/django/daphne):

```bash
daphne config.asgi:application
```

This serves both HTTP and WebSocket traffic on port `8000` by default.

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

## Authentication

All API routes require an authenticated user. The easiest way to obtain a session
is to create a superuser via `createsuperuser` and log in through the Django
admin.  The project also includes an optional Clerk middleware
(`users/middleware/clerk_auth.py`) for bearer token authentication. To enable it
uncomment the middleware entry in `config/settings.py` and pass a valid
`Authorization: Bearer <CLERK_TOKEN>` header with your requests.

## REST API

### Users

User management is handled through the Django admin interface or Clerk.  The API
itself only exposes the following user-focused endpoint:

| Method | Endpoint           | Description                      |
| ------ | ------------------ | -------------------------------- |
| `GET`  | `/api/dashboard/`  | Returns statistics about the
authenticated user and their meetings. |

### Meetings

All meeting endpoints are prefixed with `/api/` and require authentication.

| Method | Endpoint                                     | Description |
| ------ | --------------------------------------------- | ----------- |
| `GET`  | `/api/join/<room_id>/`                        | Retrieve meeting details by `room_id` UUID. |
| `GET`  | `/api/meetings/`                              | List meetings belonging to the user (admins see all). |
| `POST` | `/api/meetings/`                              | Create a new meeting. |
| `GET`  | `/api/meetings/<id>/`                         | Retrieve a single meeting. |
| `PATCH`| `/api/meetings/<id>/`                         | Update a meeting. |
| `DELETE`| `/api/meetings/<id>/`                        | Delete a meeting. |
| `POST` | `/api/meetings/<id>/set-status/`              | Change meeting status (`active`/`ended`). |
| `GET`  | `/api/meetings/<id>/messages/`                | List all messages for the meeting. |
| `POST` | `/api/meetings/<id>/messages/`                | Create a new message. |
| `GET`  | `/api/meetings/<id>/recordings/`              | List meeting recordings. |
| `POST` | `/api/meetings/<id>/recordings/`              | Upload a recording URL. |
| `POST` | `/api/meetings/<id>/mute-audio/`              | Mute the authenticated user's microphone. |
| `POST` | `/api/meetings/<id>/stop-video/`              | Stop the authenticated user's video stream. |
| `POST` | `/api/meetings/<id>/stop-call/`               | Mark that the user has left the call. |
| `GET`  | `/api/meetings/upcoming/`                     | List upcoming meetings for the user. |
| `GET`  | `/api/meetings/previous/`                     | List past/ended meetings for the user. |

WebSocket communication for live chat is available at
`/ws/meetings/<room_id>/` (handled by `ChatConsumer`).

## Environment Variables

The following variables configure the production environment (defaults are shown
in `docker-compose.yml` and `dockerfile`):

| Variable             | Description                                  |
| -------------------- | -------------------------------------------- |
| `DJANGO_SECRET_KEY`  | Secret key used by Django.                   |
| `DJANGO_DEBUG`       | Set to `False` in production.                |
| `POSTGRES_DB`        | PostgreSQL database name.                    |
| `POSTGRES_USER`      | PostgreSQL user.                             |
| `POSTGRES_PASSWORD`  | PostgreSQL user's password.                  |
| `POSTGRES_HOST`      | Database host (e.g. `db`).                   |
| `POSTGRES_PORT`      | Database port, typically `5432`.             |
| `REDIS_HOST`         | Redis host for Channels.                     |
| `REDIS_PORT`         | Redis port, typically `6378`.                |

## API Schema

The project does not yet ship with an OpenAPI/Swagger specification. You can
generate one using tools such as
[Django REST Framework's schema generator](https://www.django-rest-framework.org/api-guide/schemas/)
or `drf-yasg`.
