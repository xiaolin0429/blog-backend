from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase
from django.utils import timezone

import allure
import pytest
from apps.post.models import Category, Post

User = get_user_model()


@allure.epic("文章管理")
@allure.feature("文章排序")
class PostOrderingTest(TestCase):
    def setUp(self):
        """测试数据初始化"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test Post",
            content="Test Content",
            author=self.user,
            category=self.category,
        )

    @allure.story("创建时间排序")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试文章按创建时间排序的功能")
    @pytest.mark.high
    def test_post_ordering(self):
        """测试文章排序"""
        with allure.step("创建测试数据"):
            with transaction.atomic():
                # 设置旧文章的创建时间
                old_time = timezone.now() - timedelta(hours=1)
                Post.objects.filter(pk=self.post.pk).update(created_at=old_time)

                # 创建新文章
                new_post = Post.objects.create(
                    title="New Post",
                    content="New Content",
                    author=self.user,
                    category=self.category,
                )

                # 刷新对象状态
                self.post.refresh_from_db()
                new_post.refresh_from_db()

        with allure.step("验证排序结果"):
            # 获取所有文章并验证排序
            posts = list(Post.objects.all().order_by("-created_at"))
            self.assertEqual(posts[0].pk, new_post.pk)  # 最新的文章应该在前
            self.assertEqual(posts[1].pk, self.post.pk)  # 较早的文章应该在后
