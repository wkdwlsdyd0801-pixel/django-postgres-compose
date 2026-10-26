"""Views: a landing page, a counter that writes to Postgres, and a health check."""
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render

from .models import Visit


def home(request):
    """Landing page showing how many visits Postgres has stored so far."""
    # Reading the count forces a real query, so the page doubles as a check that
    # the database connection works.
    return render(request, "home.html", {"total": Visit.objects.count()})


def visit(request):
    """Record one visit, then report the running total as JSON."""
    # Writing a row here is the whole point: after `docker compose down` and
    # `up` again, this total continues from where it left off because the rows
    # live on the named volume, not in the container's writable layer.
    Visit.objects.create()
    return JsonResponse({"total": Visit.objects.count()})


def healthz(request):
    """
    Liveness/readiness probe for Docker and Compose.

    It runs a trivial query so the probe fails when Postgres is unreachable,
    not merely when the web process is down. Returns 200 when healthy and 503
    otherwise, which is what the Compose healthcheck polls.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "unhealthy"}, status=503)
    return JsonResponse({"status": "ok"})
