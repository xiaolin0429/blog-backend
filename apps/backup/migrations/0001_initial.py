# Generated by Django 4.2.18 on 2025-02-10 14:54

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BackupConfig",
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
                (
                    "enabled",
                    models.BooleanField(default=True, verbose_name="启用自动备份"),
                ),
                (
                    "backup_type",
                    models.CharField(
                        choices=[
                            ("full", "完整备份"),
                            ("db", "数据库备份"),
                            ("files", "文件备份"),
                            ("settings", "设置备份"),
                        ],
                        default="full",
                        max_length=20,
                        verbose_name="备份类型",
                    ),
                ),
                (
                    "frequency",
                    models.CharField(
                        choices=[
                            ("daily", "每天"),
                            ("weekly", "每周"),
                            ("monthly", "每月"),
                        ],
                        default="daily",
                        max_length=20,
                        verbose_name="备份频率",
                    ),
                ),
                (
                    "retention_days",
                    models.IntegerField(default=30, verbose_name="保留天数"),
                ),
                (
                    "backup_time",
                    models.TimeField(default="02:00", verbose_name="备份时间"),
                ),
                (
                    "last_backup",
                    models.DateTimeField(blank=True, null=True, verbose_name="上次备份时间"),
                ),
                (
                    "next_backup",
                    models.DateTimeField(blank=True, null=True, verbose_name="下次备份时间"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="创建时间"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
            ],
            options={
                "verbose_name": "备份配置",
                "verbose_name_plural": "备份配置",
                "db_table": "backup_backupconfig",
            },
        ),
        migrations.CreateModel(
            name="Backup",
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
                ("name", models.CharField(max_length=100, verbose_name="备份名称")),
                (
                    "backup_type",
                    models.CharField(
                        choices=[
                            ("full", "完整备份"),
                            ("db", "数据库备份"),
                            ("files", "文件备份"),
                            ("settings", "设置备份"),
                        ],
                        default="full",
                        max_length=20,
                        verbose_name="备份类型",
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="备份描述")),
                (
                    "file_path",
                    models.CharField(max_length=255, verbose_name="备份文件路径"),
                ),
                (
                    "file_size",
                    models.BigIntegerField(default=0, verbose_name="文件大小"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "等待中"),
                            ("running", "进行中"),
                            ("completed", "已完成"),
                            ("failed", "失败"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="备份状态",
                    ),
                ),
                (
                    "error_message",
                    models.TextField(blank=True, verbose_name="错误信息"),
                ),
                (
                    "is_auto",
                    models.BooleanField(default=False, verbose_name="是否自动备份"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="创建时间"
                    ),
                ),
                (
                    "started_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="开始时间"),
                ),
                (
                    "completed_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="完成时间"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="创建者",
                    ),
                ),
            ],
            options={
                "verbose_name": "备份记录",
                "verbose_name_plural": "备份记录",
                "db_table": "backup_backup",
                "ordering": ["-created_at"],
            },
        ),
    ]
