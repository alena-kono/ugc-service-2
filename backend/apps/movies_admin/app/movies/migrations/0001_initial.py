# Generated by Django 3.2 on 2023-04-23 19:30

from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL("CREATE SCHEMA IF NOT EXISTS content;"),
    ]
