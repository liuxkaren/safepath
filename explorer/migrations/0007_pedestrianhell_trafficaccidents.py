# Generated by Django 5.0.5 on 2024-06-02 05:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("explorer", "0006_rename_total_injure_caraccidentdensity_total_injury"),
    ]

    operations = [
        migrations.CreateModel(
            name="PedestrianHell",
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
                ("administrative_area_level_1", models.TextField(max_length=5)),
                ("administrative_area_level_2", models.TextField(max_length=10)),
                ("number", models.IntegerField()),
                ("total_fatality", models.IntegerField()),
                ("total_injury", models.IntegerField()),
                ("pedestrian_fatality", models.IntegerField()),
                ("pedestrian_injury", models.IntegerField()),
            ],
            options={
                "db_table": "risk_pedestrian_hell",
            },
        ),
        migrations.CreateModel(
            name="TrafficAccidents",
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
                ("latitude", models.DecimalField(decimal_places=5, max_digits=8)),
                ("longitude", models.DecimalField(decimal_places=5, max_digits=8)),
                ("number", models.IntegerField()),
                ("fatality", models.IntegerField()),
                ("injury", models.IntegerField()),
            ],
            options={
                "db_table": "risk_traffic_accidents",
            },
        ),
    ]
