# Generated manually: Challan + lines, migrate Entry data, remove Entry.

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def forwards_copy_entries(apps, schema_editor):
    Entry = apps.get_model("entries", "Entry")
    Challan = apps.get_model("entries", "Challan")
    ChallanLine = apps.get_model("entries", "ChallanLine")
    for entry in Entry.objects.order_by("pk"):
        challan = Challan.objects.create(created_at=entry.created_at)
        ChallanLine.objects.create(
            challan=challan,
            meters=entry.meters,
            description=entry.description or "",
            sort_order=0,
        )


def backwards_noop(apps, schema_editor):
    # Data cannot be restored into Entry without loss; leave tables empty on reverse.
    ChallanLine = apps.get_model("entries", "ChallanLine")
    Challan = apps.get_model("entries", "Challan")
    ChallanLine.objects.all().delete()
    Challan.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("entries", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Challan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ChallanLine",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("meters", models.PositiveIntegerField()),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                (
                    "challan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lines",
                        to="entries.challan",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.RunPython(forwards_copy_entries, backwards_noop),
        migrations.DeleteModel(
            name="Entry",
        ),
    ]
