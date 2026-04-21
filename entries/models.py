from django.db import models


class Entry(models.Model):
    # Required meter value; must be positive.
    meters = models.PositiveIntegerField()
    # Optional free-text note about the entry.
    description = models.TextField(blank=True)
    # Auto-captured timestamp when an entry is created.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Newest entries appear first by default.
        ordering = ["-created_at"]

    def __str__(self):
        return f"Entry #{self.pk} - {self.meters} meters"
