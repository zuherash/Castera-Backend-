# Dockerfile
FROM python:3.11.8-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SECRET_KEY=dummy_secret_key \
    DJANGO_DEBUG=False \
    POSTGRES_DB=castera_db_main \
    POSTGRES_USER=castera_user_main \
    POSTGRES_PASSWORD=castera_pass_main \
    POSTGRES_HOST=db \
    POSTGRES_PORT=5432 \
    REDIS_HOST=redis \
    REDIS_PORT=6378

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/
