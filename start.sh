#!/bin/sh

echo "Waiting for db to be ready..."
while ! nc -z db 5432; do
  sleep 0.1
done

echo "DB is ready, executing Alembic upgrades..."

alembic upgrade head

echo "Starting FastAPI..."

exec uvicorn app.main:app --host 0.0.0.0 --reload

