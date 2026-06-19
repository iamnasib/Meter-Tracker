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
        total = ChallanLine.objects.filter(item__challan=self).aggregate(t=Sum("meters")).get(
            "t"
        )
        return total if total is not None else Decimal("0")

    def line_count(self) -> int:
        return ChallanLine.objects.filter(item__challan=self).count()

    def item_count(self) -> int:
        return self.items.count()

    def __str__(self) -> str:
        return f"Challan #{self.pk} — {self.total_meters()} m"


class ChallanItem(models.Model):
    """One described block on a challan; holds multiple meter lines."""

    challan = models.ForeignKey(
        Challan,
        on_delete=models.CASCADE,
        related_name="items",
    )
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        label = self.description.strip() or f"Item {self.pk}"
        return f"{label} ({self.lines.count()} lines)"


class ChallanLine(models.Model):
    """One meter reading under a challan item."""

    item = models.ForeignKey(
        ChallanItem,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    meters = models.DecimalField(max_digits=10, decimal_places=2)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"Line {self.pk} — {self.meters} m"
