# Generated by Django 4.2.18 on 2025-02-08 13:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserStatistics",
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
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("total_users", models.IntegerField(default=0, help_text="总用户数")),
                (
                    "active_users",
                    models.IntegerField(default=0, help_text="活跃用户数"),
                ),
                ("new_users", models.IntegerField(default=0, help_text="新增用户数")),
            ],
            options={
                "verbose_name": "用户统计",
                "verbose_name_plural": "用户统计",
                "db_table": "core_user_statistics",
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="VisitStatistics",
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
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("pv", models.IntegerField(default=0, help_text="页面浏览量")),
                ("uv", models.IntegerField(default=0, help_text="独立访客数")),
                ("ip_count", models.IntegerField(default=0, help_text="IP数")),
            ],
            options={
                "verbose_name": "访问统计",
                "verbose_name_plural": "访问统计",
                "db_table": "core_visit_statistics",
                "ordering": ["-date"],
            },
        ),
    ]
