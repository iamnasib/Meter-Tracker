import django.db.models.deletion
from django.db import migrations, models


def forwards_migrate_lines_to_items(apps, schema_editor):
    ChallanLine = apps.get_model("entries", "ChallanLine")
    ChallanItem = apps.get_model("entries", "ChallanItem")

    for line in ChallanLine.objects.select_related("challan").order_by(
        "challan_id", "sort_order", "id"
    ):
        item = ChallanItem.objects.create(
            challan_id=line.challan_id,
            description=line.description or "",
            sort_order=line.sort_order,
        )
        line.item_id = item.pk
        line.sort_order = 0
        line.save(update_fields=["item_id", "sort_order"])


def backwards_migrate_items_to_lines(apps, schema_editor):
    ChallanLine = apps.get_model("entries", "ChallanLine")
    ChallanItem = apps.get_model("entries", "ChallanItem")

    for item in ChallanItem.objects.order_by("challan_id", "sort_order", "id"):
        lines = ChallanLine.objects.filter(item_id=item.pk).order_by("sort_order", "id")
        for line_order, line in enumerate(lines):
            line.challan_id = item.challan_id
            line.description = item.description or ""
            line.sort_order = item.sort_order if line_order == 0 else item.sort_order + line_order
            line.save(update_fields=["challan_id", "description", "sort_order"])


class Migration(migrations.Migration):

    dependencies = [
        ("entries", "0003_alter_challanline_meters_decimal"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChallanItem",
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
                ("description", models.TextField(blank=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                (
                    "challan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="entries.challan",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.AddField(
            model_name="challanline",
            name="item",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lines",
                to="entries.challanitem",
            ),
        ),
        migrations.RunPython(
            forwards_migrate_lines_to_items,
            backwards_migrate_items_to_lines,
        ),
        migrations.RemoveField(
            model_name="challanline",
            name="challan",
        ),
        migrations.RemoveField(
            model_name="challanline",
            name="description",
        ),
        migrations.AlterField(
            model_name="challanline",
            name="item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lines",
                to="entries.challanitem",
            ),
        ),
    ]
