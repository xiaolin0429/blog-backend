from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest

from apps.backup.models import Backup
from apps.core.models import FileStorage
from apps.overview.services import SystemService
from apps.post.models import Comment, Post

User = get_user_model()


@pytest.fixture
def mock_psutil():
    with patch("apps.overview.services.psutil") as mock:
        # 模拟进程信息
        mock.Process.return_value.create_time.return_value = 1644451200.0

        # 模拟CPU信息
        mock.cpu_percent.return_value = 45.6
        mock.cpu_count.side_effect = [8, 4]  # 第一次调用返回8（总核心），第二次调用返回4（物理核心）

        # 模拟内存信息
        mock_memory = MagicMock()
        mock_memory.percent = 32.1
        mock_memory.total = 17179869184
        mock_memory.available = 8589934592
        mock_memory.used = 8589934592
        mock.virtual_memory.return_value = mock_memory

        # 模拟磁盘信息
        mock_disk = MagicMock()
        mock_disk.percent = 68.9
        mock_disk.total = 1099511627776
        mock_disk.used = 757573918208
        mock_disk.free = 341937709568
        mock.disk_usage.return_value = mock_disk

        yield mock


@pytest.fixture
def test_data(django_user_model):
    # 创建测试用户
    user = django_user_model.objects.create_user(
        username="testuser", password="testpass"
    )

    # 创建测试文章
    post1 = Post.objects.create(
        title="Test Post 1", content="Content 1", author=user, status="published"
    )
    post2 = Post.objects.create(
        title="Test Post 2", content="Content 2", author=user, status="draft"
    )

    # 创建测试评论
    comment = Comment.objects.create(post=post1, author=user, content="Test Comment")

    # 创建测试文件存储
    file_storage = FileStorage.objects.create(
        file_id="test123",
        original_name="test.txt",
        file_type="txt",
        mime_type="text/plain",
        file_size=1024,
        file_content=b"test content",
    )

    # 创建测试备份
    backup = Backup.objects.create(
        name="Test Backup", backup_type="full", status="completed", created_by=user
    )

    return {
        "user": user,
        "post1": post1,
        "post2": post2,
        "comment": comment,
        "file_storage": file_storage,
        "backup": backup,
    }


@pytest.mark.django_db
class TestSystemService:
    def test_get_system_info(self, mock_psutil):
        """测试获取系统信息"""
        info = SystemService.get_system_info()

        assert info["version"] == "1.0.0"
        assert info["start_time"] == 1644451200.0
        assert isinstance(info["python_version"], str)

        assert info["cpu_usage"]["percent"] == 45.6
        assert info["cpu_usage"]["cores"] == 8
        assert info["cpu_usage"]["physical_cores"] == 4

        assert info["memory_usage"]["percent"] == 32.1
        assert info["memory_usage"]["total"] == 17179869184
        assert info["memory_usage"]["available"] == 8589934592
        assert info["memory_usage"]["used"] == 8589934592

        assert info["disk_usage"]["percent"] == 68.9
        assert info["disk_usage"]["total"] == 1099511627776
        assert info["disk_usage"]["used"] == 757573918208
        assert info["disk_usage"]["free"] == 341937709568

        assert "timestamp" in info

    def test_get_content_stats(self, test_data):
        """测试获取内容统计"""
        stats = SystemService.get_content_stats()

        assert stats["total_users"] == 1
        assert stats["total_posts"] == 2
        assert stats["published_posts"] == 1
        assert stats["total_comments"] == 1
        assert "timestamp" in stats

    def test_get_storage_stats(self, test_data):
        """测试获取存储统计"""
        stats = SystemService.get_storage_stats()

        assert stats["total_files"] == 1
        assert stats["total_size"] == 1024  # 文件大小
        assert stats["backup_count"] == 1
        assert stats["last_backup"] is not None
        assert stats["last_backup"]["name"] == "Test Backup"
        assert stats["last_backup"]["status"] == "completed"
        assert "timestamp" in stats

    def test_get_recent_activities(self, test_data):
        """测试获取最近活动"""
        activities = SystemService.get_recent_activities()

        assert len(activities["recent_posts"]) == 2
        assert activities["recent_posts"][0]["title"] == "Test Post 2"  # 最新的文章
        assert activities["recent_posts"][1]["title"] == "Test Post 1"

        assert len(activities["recent_backups"]) == 1
        assert activities["recent_backups"][0]["name"] == "Test Backup"
        assert "timestamp" in activities
