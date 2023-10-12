# Generated by Django 4.2.6 on 2023-10-11 15:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("companies", "0004_add_ordering"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="company",
            options={"ordering": ("name",), "verbose_name": "company", "verbose_name_plural": "companies"},
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="department name")),
                (
                    "point",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="departments",
                        to="companies.point",
                        verbose_name="point",
                    ),
                ),
            ],
            options={
                "verbose_name": "department",
                "verbose_name_plural": "departments",
                "ordering": ("name",),
            },
        ),
    ]
