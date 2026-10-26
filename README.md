# django-postgres-compose

A Django app and a PostgreSQL database wired together with Docker Compose, where the database files live on a **named volume** so they persist across container restarts.

## Highlights

- `db` (postgres:16) + `web` (Django) orchestrated by one `docker compose up`.
- Postgres data on a named volume (`pg-data`) — `docker compose down && up` keeps the data.
- `web` waits for the database via a `pg_isready` healthcheck and `depends_on: service_healthy`.
- All connection settings come from the environment; nothing secret is baked into the image.

## Run

```bash
cp .env.example .env            # then set DJANGO_SECRET_KEY and POSTGRES_PASSWORD
docker compose up --build
```

Open http://127.0.0.1:8000/ and click "Record a visit". Then prove persistence:

```bash
docker compose down            # stop and remove containers (volume is kept)
docker compose up              # the visit count continues from before
```

### Run the tests

```bash
docker compose run --rm web python manage.py test
```
