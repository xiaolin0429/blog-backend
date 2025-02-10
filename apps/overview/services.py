import logging
import os
import platform
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.utils import timezone

import psutil

User = get_user_model()
logger = logging.getLogger(__name__)


class SystemService:
    """系统服务类"""

    @classmethod
    def get_system_info(cls):
        """获取系统基本信息"""
        try:
            # 获取进程信息
            process = psutil.Process(os.getpid())

            # 获取CPU使用率（interval=None 表示获取当前瞬时值）
            cpu_percent = psutil.cpu_percent(interval=None)

            # 获取内存使用情况
            memory = psutil.virtual_memory()

            # 获取磁盘使用情况 - 使用项目所在磁盘的根路径
            root_path = os.path.abspath(os.sep)  # 获取根路径 '/'
            if platform.system() == "Darwin":  # macOS
                root_path = "/System/Volumes/Data"  # macOS的实际根目录
            disk = psutil.disk_usage(root_path)

            return {
                "version": getattr(settings, "VERSION", "1.0.0"),
                "start_time": process.create_time(),
                "python_version": platform.python_version(),
                "cpu_usage": {
                    "percent": cpu_percent,
                    "cores": psutil.cpu_count(),
                    "physical_cores": psutil.cpu_count(logical=False),
                },
                "memory_usage": {
                    "percent": memory.percent,
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                },
                "disk_usage": {
                    "percent": disk.percent,
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                },
                "timestamp": timezone.now().timestamp(),
            }
        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}", exc_info=True)
            return {
                "version": getattr(settings, "VERSION", "1.0.0"),
                "python_version": platform.python_version(),
                "error": str(e),
                "timestamp": timezone.now().timestamp(),
            }

    @classmethod
    def get_content_stats(cls):
        """获取内容统计信息"""
        from apps.post.models import Comment, Post

        now = timezone.now()
        last_week = now - timedelta(days=7)

        return {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(last_login__gte=last_week).count(),
            "total_posts": Post.objects.count(),
            "published_posts": Post.objects.filter(status="published").count(),
            "total_comments": Comment.objects.count(),
            "recent_comments": Comment.objects.filter(
                created_at__gte=last_week
            ).count(),
            "timestamp": now.timestamp(),
        }

    @classmethod
    def get_storage_stats(cls):
        """获取存储统计信息"""
        from apps.backup.models import Backup
        from apps.core.models import FileStorage

        now = timezone.now()
        last_backup = (
            Backup.objects.filter(status="completed").order_by("-created_at").first()
        )

        return {
            "total_files": FileStorage.objects.count(),
            "total_size": FileStorage.objects.aggregate(total_size=Sum("file_size"))[
                "total_size"
            ]
            or 0,
            "backup_count": Backup.objects.count(),
            "last_backup": {
                "id": last_backup.id if last_backup else None,
                "name": last_backup.name if last_backup else None,
                "created_at": last_backup.created_at if last_backup else None,
                "status": last_backup.status if last_backup else None,
                "status_display": last_backup.get_status_display()
                if last_backup
                else None,
            }
            if last_backup
            else None,
            "timestamp": now.timestamp(),
        }

    @classmethod
    def get_recent_activities(cls):
        """获取最近活动"""
        from apps.backup.models import Backup
        from apps.post.models import Post

        now = timezone.now()
        recent_posts = Post.objects.select_related("author").order_by("-created_at")[:5]

        recent_backups = Backup.objects.order_by("-created_at")[:5]

        return {
            "recent_posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "author": post.author.username,
                    "created_at": post.created_at,
                    "status": post.status,
                    "status_display": post.get_status_display(),
                }
                for post in recent_posts
            ],
            "recent_backups": [
                {
                    "id": backup.id,
                    "name": backup.name,
                    "created_at": backup.created_at,
                    "status": backup.status,
                    "status_display": backup.get_status_display(),
                }
                for backup in recent_backups
            ],
            "timestamp": now.timestamp(),
        }
