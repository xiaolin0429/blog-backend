# Generated by Django 4.2.18 on 2025-02-15 10:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("post", "0006_post_cover"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="cover",
            field=models.CharField(
                blank=True, max_length=500, null=True, verbose_name="封面图"
            ),
        ),
    ]
