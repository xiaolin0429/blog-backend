# Generated manually

from django.db import migrations


def noop(apps, schema_editor):
    """Do nothing, just for recording the migration"""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(noop, noop),
    ]
