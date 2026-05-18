from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Challan(models.Model):
    """Parent record (e.g. one challan / bill page for a client)."""

    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def total_meters(self) -> Decimal:
        total = self.lines.aggregate(t=Sum("meters")).get("t")
        return total if total is not None else Decimal("0")

    def line_count(self) -> int:
        return self.lines.count()

    def __str__(self) -> str:
        return f"Challan #{self.pk} — {self.total_meters()} m"


class ChallanLine(models.Model):
    """One line item: meters (required) and optional description."""

    challan = models.ForeignKey(
        Challan,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    meters = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"Line {self.pk} — {self.meters} m"
