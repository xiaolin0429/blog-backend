from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from celery import shared_task

from .models import Backup, BackupConfig
from .services import BackupService


@shared_task
def create_auto_backup():
    """创建自动备份"""
    try:
        # 获取所有启用的备份配置
        configs = BackupConfig.objects.filter(enabled=True)

        for config in configs:
            # 检查是否需要执行备份
            if not config.next_backup or timezone.now() >= config.next_backup:
                name = f"自动备份 {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
                description = f"系统自动创建的{config.get_backup_type_display()}"

                # 创建备份
                backup = BackupService.create_backup(
                    name=name, backup_type=config.backup_type, description=description
                )
                backup.is_auto = True
                backup.save()

                # 如果是完整备份或文件备份，则备份媒体文件
                if config.backup_type in ["full", "files"]:
                    BackupService.backup_media_files(backup)

                # 更新配置的备份时间
                config.last_backup = timezone.now()

                # 计算下次备份时间
                if config.frequency == "hourly":
                    next_backup = timezone.now() + timedelta(hours=1)
                elif config.frequency == "daily":
                    next_backup = timezone.now() + timedelta(days=1)
                elif config.frequency == "weekly":
                    next_backup = timezone.now() + timedelta(weeks=1)
                else:  # monthly
                    next_backup = timezone.now() + timedelta(days=30)

                config.next_backup = next_backup
                config.save()

        # 清理过期的自动备份
        cleanup_old_backups()

        return "自动备份任务完成"
    except Exception as e:
        return f"自动备份任务失败：{str(e)}"


@shared_task
def cleanup_old_backups():
    """清理过期的备份"""
    try:
        # 获取所有备份配置
        configs = BackupConfig.objects.all()

        for config in configs:
            # 获取此类型的自动备份
            old_backups = Backup.objects.filter(
                backup_type=config.backup_type,
                is_auto=True,
                created_at__lt=timezone.now() - timedelta(days=config.retention_days),
            ).order_by("-created_at")

            # 删除过期备份
            old_backups.delete()

        return "清理过期备份完成"
    except Exception as e:
        return f"清理过期备份失败：{str(e)}"
