# Generated by Django 5.1.6 on 2025-04-10 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0003_alter_maison_id_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="maison",
            name="points",
            field=models.IntegerField(default=0),
        ),
    ]
