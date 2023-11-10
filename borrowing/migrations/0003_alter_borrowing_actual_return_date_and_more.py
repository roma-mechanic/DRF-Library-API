# Generated by Django 4.2.7 on 2023-11-07 19:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("borrowing", "0002_alter_borrowing_options_borrowing_is_active_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="expected_return_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
