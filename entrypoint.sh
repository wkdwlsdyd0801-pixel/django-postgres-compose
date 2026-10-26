#!/bin/sh
# Container entrypoint: wait for Postgres, apply migrations, then run gunicorn.
set -e

# The web container usually starts before Postgres is ready to accept queries.
# Compose's `depends_on: condition: service_healthy` covers the normal case,
# but we poll here too so the app never crashes on a transient early failure.
echo "Waiting for Postgres at ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
until python -c "
import os, sys, psycopg
try:
    psycopg.connect(
        host=os.environ.get('POSTGRES_HOST', 'db'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
        connect_timeout=2,
    ).close()
except Exception:
    sys.exit(1)
"; do
    sleep 1
done
echo "Postgres is up."

# Apply outstanding migrations against the Postgres database.
python manage.py migrate --noinput

# exec replaces the shell so gunicorn becomes PID 1 and receives SIGTERM from
# `docker stop` directly, allowing a clean graceful shutdown.
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --access-logfile - \
    --error-logfile -
