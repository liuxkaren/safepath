# Generated by Django 5.0.5 on 2024-05-26 03:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("explorer", "0002_userinfo"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="caraccident",
            table="risk_car_accident",
        ),
        migrations.AlterModelTable(
            name="density",
            table="risk_car_accident_density",
        ),
        migrations.AlterModelTable(
            name="earthquake",
            table="risk_earthquake",
        ),
        migrations.AlterModelTable(
            name="intensity",
            table="risk_earthquake_intensity",
        ),
    ]
