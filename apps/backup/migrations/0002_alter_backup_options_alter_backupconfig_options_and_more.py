# Generated by Django 4.2.18 on 2025-02-10 15:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("backup", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="backup",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "备份",
                "verbose_name_plural": "备份",
            },
        ),
        migrations.AlterModelOptions(
            name="backupconfig",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "备份配置",
                "verbose_name_plural": "备份配置",
            },
        ),
        migrations.AlterField(
            model_name="backup",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
        ),
        migrations.AlterField(
            model_name="backup",
            name="created_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="backups",
                to=settings.AUTH_USER_MODEL,
                verbose_name="创建者",
            ),
        ),
        migrations.AlterField(
            model_name="backup",
            name="file_path",
            field=models.FileField(upload_to="backups/", verbose_name="备份文件"),
        ),
        migrations.AlterField(
            model_name="backup",
            name="name",
            field=models.CharField(max_length=255, verbose_name="备份名称"),
        ),
        migrations.AlterField(
            model_name="backup",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "等待中"),
                    ("running", "进行中"),
                    ("completed", "已完成"),
                    ("failed", "失败"),
                ],
                default="pending",
                max_length=20,
                verbose_name="状态",
            ),
        ),
        migrations.AlterField(
            model_name="backupconfig",
            name="backup_time",
            field=models.TimeField(default="02:00:00", verbose_name="备份时间"),
        ),
        migrations.AlterField(
            model_name="backupconfig",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
        ),
        migrations.AlterField(
            model_name="backupconfig",
            name="enabled",
            field=models.BooleanField(default=True, verbose_name="是否启用"),
        ),
        migrations.AlterField(
            model_name="backupconfig",
            name="frequency",
            field=models.CharField(
                choices=[
                    ("hourly", "每小时"),
                    ("daily", "每天"),
                    ("weekly", "每周"),
                    ("monthly", "每月"),
                ],
                default="daily",
                max_length=20,
                verbose_name="频率",
            ),
        ),
    ]
