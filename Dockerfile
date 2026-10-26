# Small, single-stage image for the web service. The database runs in its own
# official Postgres container (see docker-compose.yml), so this image only needs
# the Django app and its Python dependencies.
FROM python:3.12-slim

# Don't write .pyc files; stream stdout/stderr straight to the container logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first so this layer is cached unless the deps change.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create an unprivileged user; the app must never run as root in the container.
RUN groupadd --gid 10001 appuser && \
    useradd --uid 10001 --gid appuser --no-create-home --home-dir /app appuser

# Copy the application code and hand ownership to the unprivileged user.
COPY --chown=appuser:appuser . .

# entrypoint.sh must stay executable when run as the non-root user.
RUN chmod +x entrypoint.sh

USER appuser

EXPOSE 8000

# entrypoint.sh waits for Postgres, applies migrations, then execs gunicorn.
ENTRYPOINT ["./entrypoint.sh"]
