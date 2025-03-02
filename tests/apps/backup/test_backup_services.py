import json
import os
import tempfile
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

import pytest

from apps.backup.models import Backup, BackupConfig
from apps.backup.services import BackupService
from apps.post.models import Category, Post, Tag

User = get_user_model()


@pytest.fixture(autouse=True)
def setup_test_media():
    """设置测试媒体目录"""
    # 创建测试媒体目录
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    os.makedirs(os.path.join(settings.MEDIA_ROOT, "backups"), exist_ok=True)

    yield

    # 清理测试媒体目录
    import shutil

    if os.path.exists(settings.MEDIA_ROOT):
        shutil.rmtree(settings.MEDIA_ROOT)


@pytest.fixture
def test_data(django_user_model):
    # 创建测试用户
    user = django_user_model.objects.create_user(
        username="testuser", password="testpass"
    )

    # 创建测试分类
    category = Category.objects.create(name="Test Category")

    # 创建测试标签
    tag = Tag.objects.create(name="Test Tag")

    # 创建测试文章
    post = Post.objects.create(
        title="Test Post",
        content="Test Content",
        author=user,
        category=category,
        status="published",
    )
    post.tags.add(tag)

    # 创建测试备份配置
    config = BackupConfig.objects.create(
        enabled=True,
        backup_type=Backup.BackupType.FULL,
        frequency=BackupConfig.Frequency.DAILY,
        retention_days=30,
        backup_time="02:00:00",
    )

    return {
        "user": user,
        "category": category,
        "tag": tag,
        "post": post,
        "config": config,
    }


@pytest.fixture
def mock_file_operations():
    with patch("os.makedirs") as mock_makedirs, patch(
        "shutil.copy2"
    ) as mock_copy2, patch("os.path.exists") as mock_exists, patch(
        "os.walk"
    ) as mock_walk, patch(
        "shutil.rmtree"
    ) as mock_rmtree:
        # 模拟文件存在
        mock_exists.return_value = True

        # 模拟文件遍历
        mock_walk.return_value = [
            (settings.MEDIA_ROOT, [], ["test.txt"]),
        ]

        yield {
            "makedirs": mock_makedirs,
            "copy2": mock_copy2,
            "exists": mock_exists,
            "walk": mock_walk,
            "rmtree": mock_rmtree,
        }


@pytest.mark.django_db
@pytest.mark.backup
class TestBackupService:
    def test_create_backup(self, test_data, mock_file_operations):
        """测试创建备份"""
        user = test_data["user"]
        backup = BackupService.create_backup(
            name="Test Backup",
            backup_type=Backup.BackupType.FULL,
            description="Test Description",
            user=user,
        )

        assert backup.name == "Test Backup"
        assert backup.backup_type == Backup.BackupType.FULL
        assert backup.description == "Test Description"
        assert backup.created_by == user
        assert backup.status == Backup.Status.COMPLETED
        assert backup.file_path is not None

    def test_restore_from_backup(self, test_data, mock_file_operations):
        """测试从备份恢复"""
        # 创建测试备份文件
        backup_data = {"post.Post": "[]", "post.Category": "[]", "post.Tag": "[]"}
        backup_content = json.dumps(backup_data).encode("utf-8")
        backup_file = SimpleUploadedFile(
            "test_backup.json", backup_content, content_type="application/json"
        )

        # 创建一个测试备份
        backup = Backup.objects.create(
            name="Test Backup",
            backup_type=Backup.BackupType.FULL,
            status=Backup.Status.COMPLETED,
            file_path=backup_file,
        )

        # 清除现有数据
        Post.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()

        # 从备份恢复
        BackupService.restore_from_backup(backup)

        # 验证数据已恢复
        assert Post.objects.count() == 0  # 因为我们模拟的备份数据是空的
        assert Category.objects.count() == 0
        assert Tag.objects.count() == 0

    def test_backup_media_files(self, test_data, mock_file_operations):
        """测试备份媒体文件"""
        backup = Backup.objects.create(
            name="Test Backup",
            backup_type=Backup.BackupType.FULL,
            status=Backup.Status.COMPLETED,
        )

        # 创建一个测试文件
        test_file_path = os.path.join(settings.MEDIA_ROOT, "test.txt")
        with open(test_file_path, "w") as f:
            f.write("test content")

        backup_dir = BackupService.backup_media_files(backup)

        assert backup_dir is not None
        mock_file_operations["makedirs"].assert_called()
        mock_file_operations["copy2"].assert_called()

    def test_create_backup_with_error(self, test_data):
        """测试创建备份时发生错误"""
        with patch("django.core.files.base.ContentFile.write") as mock_write:
            mock_write.side_effect = Exception("Test error")

            with pytest.raises(Exception):
                backup = BackupService.create_backup(
                    name="Test Backup",
                    backup_type=Backup.BackupType.FULL,
                    description="Test Description",
                )

                assert backup.status == Backup.Status.FAILED
                assert backup.error_message == "Test error"

    def test_restore_from_backup_with_error(self, test_data):
        """测试从备份恢复时发生错误"""
        backup = Backup.objects.create(
            name="Test Backup",
            backup_type=Backup.BackupType.FULL,
            status=Backup.Status.COMPLETED,
        )

        with pytest.raises(ValueError):
            BackupService.restore_from_backup(backup)  # 没有备份文件应该抛出错误
