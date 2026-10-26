"""Tests run against a real Postgres database (the Django test runner creates
a throwaway test DB on the same server), so they also exercise the driver."""
from django.test import TestCase
from django.urls import reverse

from .models import Visit


class VisitTests(TestCase):
    def test_visit_persists_a_row(self):
        # Each call to /visit/ should add exactly one row and report the total.
        self.assertEqual(Visit.objects.count(), 0)
        response = self.client.get(reverse("visit"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(Visit.objects.count(), 1)

    def test_healthz_ok_when_db_reachable(self):
        # With the test DB up, the health check must report ok.
        response = self.client.get(reverse("healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
