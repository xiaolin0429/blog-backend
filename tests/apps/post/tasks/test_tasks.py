from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

import allure
import pytest
from apps.post.models import Post
from apps.post.tasks import cleanup_auto_save_versions

User = get_user_model()


@allure.epic("文章管理")
@allure.feature("自动保存清理")
class AutoSaveCleanupTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        with allure.step("创建一个有31天前自动保存内容的文章"):
            self.old_post = Post.objects.create(
                title="Old Post", content="Old Content", author=self.user
            )
            old_time = timezone.now() - timedelta(days=31)
            self.old_post.auto_save_content = {
                "title": "Auto Saved Title",
                "content": "Auto Saved Content",
                "excerpt": "Auto Saved Excerpt",
                "version": 1,
                "auto_save_time": old_time.isoformat(),
            }
            self.old_post.save()

        with allure.step("创建一个有最近自动保存内容的文章"):
            self.recent_post = Post.objects.create(
                title="Recent Post", content="Recent Content", author=self.user
            )
            recent_time = timezone.now() - timedelta(days=1)
            self.recent_post.auto_save_content = {
                "title": "Recent Auto Saved Title",
                "content": "Recent Auto Saved Content",
                "excerpt": "Recent Auto Saved Excerpt",
                "version": 1,
                "auto_save_time": recent_time.isoformat(),
            }
            self.recent_post.save()

    @allure.story("定时清理")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试清理30天前的自动保存内容，保留最近30天的内容")
    @pytest.mark.scheduled
    def test_cleanup_auto_save_versions(self):
        """测试清理自动保存版本的任务"""
        with allure.step("运行清理任务"):
            result = cleanup_auto_save_versions()

        with allure.step("验证旧文章的自动保存内容"):
            old_post = Post.objects.get(id=self.old_post.id)
            self.assertIsNone(old_post.auto_save_content)

        with allure.step("验证最近文章的自动保存内容"):
            recent_post = Post.objects.get(id=self.recent_post.id)
            self.assertIsNotNone(recent_post.auto_save_content)
            self.assertEqual(
                recent_post.auto_save_content["title"], "Recent Auto Saved Title"
            )

        with allure.step("验证返回消息"):
            self.assertEqual(result, "已清理 1 篇文章的自动保存内容") 