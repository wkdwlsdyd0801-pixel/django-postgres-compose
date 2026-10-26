"""
Django settings for the Postgres + Docker Compose demo.

The focus of this project is wiring Django to a PostgreSQL container through
Docker Compose, with the database files kept on a named volume so they survive
container restarts. Everything the app needs to reach the database comes from
environment variables, so the same image runs locally and in CI unchanged.
See .env.example for the variables Compose injects.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default="false"):
    # Treat the usual truthy spellings as True; everything else is False.
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


# SECRET_KEY is supplied at runtime; the fallback is obviously insecure so a
# missing value is noticed in dev instead of silently shipping a known default.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")

# DEBUG defaults to False: a container should never run in debug unless asked.
DEBUG = env_bool("DJANGO_DEBUG", "false")

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "web",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

# The database connection is built entirely from environment variables. In
# Compose, POSTGRES_HOST is the service name "db", which Docker's internal DNS
# resolves to the Postgres container; the data itself lives on a named volume
# mounted inside that container, not here.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "appdb"),
        "USER": os.environ.get("POSTGRES_USER", "appuser"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        # Reuse connections for 60s instead of opening one per request; a small
        # but real win when the DB lives one network hop away in another container.
        "CONN_MAX_AGE": int(os.environ.get("DJANGO_CONN_MAX_AGE", "60")),
    }
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # Log to stdout so the container runtime collects the logs.
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO")},
}
