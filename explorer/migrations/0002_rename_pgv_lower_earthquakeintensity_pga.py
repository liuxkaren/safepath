# Generated by Django 5.0.5 on 2024-06-04 07:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("explorer", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="earthquakeintensity",
            old_name="pgv_lower",
            new_name="pga",
        ),
    ]