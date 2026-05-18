from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("entries", "0002_challan_challanline_remove_entry"),
    ]

    operations = [
        migrations.AlterField(
            model_name="challanline",
            name="meters",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
