from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Backup(models.Model):
    """备份记录模型"""

    class BackupType(models.TextChoices):
        FULL = "full", _("完整备份")
        DB = "db", _("数据库备份")
        FILES = "files", _("文件备份")
        SETTINGS = "settings", _("设置备份")

    class Status(models.TextChoices):
        PENDING = "pending", _("等待中")
        RUNNING = "running", _("进行中")
        COMPLETED = "completed", _("已完成")
        FAILED = "failed", _("失败")

    name = models.CharField(_("备份名称"), max_length=255)
    backup_type = models.CharField(
        _("备份类型"), max_length=20, choices=BackupType.choices, default=BackupType.FULL
    )
    description = models.TextField(_("备份描述"), blank=True)
    file_path = models.FileField(_("备份文件"), upload_to="backups/")
    file_size = models.BigIntegerField(_("文件大小"), default=0)
    status = models.CharField(
        _("状态"), max_length=20, choices=Status.choices, default=Status.PENDING
    )
    error_message = models.TextField(_("错误信息"), blank=True)
    is_auto = models.BooleanField(_("是否自动备份"), default=False)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    started_at = models.DateTimeField(_("开始时间"), null=True, blank=True)
    completed_at = models.DateTimeField(_("完成时间"), null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        verbose_name=_("创建者"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="backups",
    )

    class Meta:
        app_label = "backup"
        verbose_name = _("备份")
        verbose_name_plural = _("备份")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class BackupConfig(models.Model):
    """备份配置模型"""

    class Frequency(models.TextChoices):
        HOURLY = "hourly", _("每小时")
        DAILY = "daily", _("每天")
        WEEKLY = "weekly", _("每周")
        MONTHLY = "monthly", _("每月")

    enabled = models.BooleanField(_("是否启用"), default=True)
    backup_type = models.CharField(
        _("备份类型"),
        max_length=20,
        choices=Backup.BackupType.choices,
        default=Backup.BackupType.FULL,
    )
    frequency = models.CharField(
        _("频率"), max_length=20, choices=Frequency.choices, default=Frequency.DAILY
    )
    retention_days = models.IntegerField(_("保留天数"), default=30)
    backup_time = models.TimeField(_("备份时间"), default="02:00:00")
    last_backup = models.DateTimeField(_("上次备份时间"), null=True, blank=True)
    next_backup = models.DateTimeField(_("下次备份时间"), null=True, blank=True)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)

    class Meta:
        app_label = "backup"
        verbose_name = _("备份配置")
        verbose_name_plural = _("备份配置")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_backup_type_display()} - {self.get_frequency_display()}"
