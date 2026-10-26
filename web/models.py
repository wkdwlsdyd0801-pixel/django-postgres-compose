"""A single tiny model used to prove the Postgres data actually persists."""
from django.db import models


class Visit(models.Model):
    # One row per visit to /visit/. The row count is what we read back after a
    # restart: if it keeps growing, the named volume is doing its job.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
