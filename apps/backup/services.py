import json
import os
import shutil
from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.core import serializers
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.backup.models import Backup


class BackupService:
    """备份服务类"""

    BACKUP_MODELS = {
        Backup.BackupType.FULL: [
            "post.Post",
            "post.Category",
            "post.Tag",
            "user.User",
        ],
        Backup.BackupType.DB: [
            "post.Post",
            "post.Category",
            "post.Tag",
        ],
        Backup.BackupType.SETTINGS: [
            "backup.BackupConfig",
        ],
    }

    @classmethod
    def create_backup(
        cls, name, backup_type=Backup.BackupType.FULL, description="", user=None
    ):
        """创建数据备份"""

        # 创建备份记录
        backup = Backup.objects.create(
            name=name,
            backup_type=backup_type,
            description=description,
            created_by=user,
            status=Backup.Status.RUNNING,
            started_at=datetime.now(),
        )

        try:
            backup_data = {}

            # 根据备份类型选择要备份的模型
            models_to_backup = cls.BACKUP_MODELS.get(backup_type, [])

            # 导出数据库数据
            for model_path in models_to_backup:
                app_label, model_name = model_path.split(".")
                model = apps.get_model(app_label, model_name)
                backup_data[model_path] = serializers.serialize(
                    "json", model.objects.all()
                )

            # 创建备份文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{backup_type}_{timestamp}.json"

            # 将数据写入JSON文件
            backup.file_path.save(
                filename,
                ContentFile(
                    json.dumps(backup_data, ensure_ascii=False, indent=2).encode(
                        "utf-8"
                    )
                ),
            )

            # 如果是完整备份或文件备份，同时备份媒体文件
            if backup_type in [Backup.BackupType.FULL, Backup.BackupType.FILES]:
                cls.backup_media_files(backup)

            # 更新备份状态
            backup.status = Backup.Status.COMPLETED
            backup.completed_at = datetime.now()
            backup.file_size = backup.file_path.size
            backup.save()

            return backup

        except Exception as e:
            backup.status = Backup.Status.FAILED
            backup.error_message = str(e)
            backup.completed_at = datetime.now()
            backup.save()
            raise

    @classmethod
    @transaction.atomic
    def restore_from_backup(cls, backup_instance):
        """从备份文件恢复数据"""
        if not backup_instance.file_path:
            raise ValueError(_("备份文件不存在"))

        if backup_instance.status != Backup.Status.COMPLETED:
            raise ValueError(_("备份未完成，无法恢复"))

        # 更新状态为进行中
        backup_instance.status = Backup.Status.RUNNING
        backup_instance.started_at = datetime.now()
        backup_instance.save()

        try:
            # 读取备份文件
            backup_data = json.loads(backup_instance.file_path.read().decode("utf-8"))

            # 根据备份类型选择要恢复的模型
            models_to_restore = cls.BACKUP_MODELS.get(backup_instance.backup_type, [])

            # 清空现有数据
            for model_path in models_to_restore:
                app_label, model_name = model_path.split(".")
                model = apps.get_model(app_label, model_name)
                model.objects.all().delete()

            # 恢复数据
            for model_path, data in backup_data.items():
                if model_path not in models_to_restore:
                    continue

                app_label, model_name = model_path.split(".")
                model = apps.get_model(app_label, model_name)

                objects = serializers.deserialize("json", data)
                for obj in objects:
                    obj.save()

            # 更新状态为已完成
            backup_instance.status = Backup.Status.COMPLETED
            backup_instance.completed_at = datetime.now()
            backup_instance.save()

        except Exception as e:
            backup_instance.status = Backup.Status.FAILED
            backup_instance.error_message = str(e)
            backup_instance.completed_at = datetime.now()
            backup_instance.save()
            raise

    @classmethod
    def backup_media_files(cls, backup_instance):
        """备份媒体文件"""
        if backup_instance.backup_type not in [
            Backup.BackupType.FULL,
            Backup.BackupType.FILES,
        ]:
            return None

        media_dir = settings.MEDIA_ROOT
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(settings.MEDIA_ROOT, "backups", f"media_{timestamp}")

        try:
            # 创建备份目录
            os.makedirs(backup_dir, exist_ok=True)

            # 复制媒体文件
            for root, dirs, files in os.walk(media_dir):
                # 将 PosixPath 转换为字符串
                root_str = str(root)

                # 跳过备份目录
                if "backups" in root_str.split(os.path.sep):
                    continue

                for file in files:
                    src_path = os.path.join(root_str, file)
                    rel_path = os.path.relpath(src_path, media_dir)
                    dst_path = os.path.join(backup_dir, rel_path)

                    # 创建目标目录（如果不存在）
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    # 复制文件
                    shutil.copy2(src_path, dst_path)

            return backup_dir

        except Exception as e:
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            raise
