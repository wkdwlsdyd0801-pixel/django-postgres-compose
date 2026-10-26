"""URL routing: a landing page, a DB-backed counter, and a health check."""
from django.urls import path

from web import views

urlpatterns = [
    path("", views.home, name="home"),
    # Each visit writes a row to Postgres, proving the named volume keeps data
    # across container restarts.
    path("visit/", views.visit, name="visit"),
    path("healthz", views.healthz, name="healthz"),
]
