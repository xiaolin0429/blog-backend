from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase
from django.utils import timezone

import allure
import pytest
from apps.post.models import Category, Comment, Post


@allure.epic("评论管理")
@allure.feature("评论模型")
class CommentModelTest(TestCase):
    """评论模型测试"""

    def setUp(self):
        User = get_user_model()
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
        self.comment = Comment.objects.create(
            post=self.post, author=self.user, content="Test Comment"
        )

    @allure.story("评论创建")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试评论创建时各个字段的基本属性")
    @pytest.mark.high
    def test_comment_creation(self):
        """测试评论创建"""
        with allure.step("验证评论属性"):
            self.assertEqual(self.comment.content, "Test Comment")
            self.assertEqual(self.comment.author, self.user)
            self.assertEqual(self.comment.post, self.post)
            self.assertIsNone(self.comment.parent)

    @allure.story("评论基础功能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试评论的字符串表示方法")
    @pytest.mark.medium
    def test_comment_str_representation(self):
        """测试评论字符串表示"""
        with allure.step("验证评论字符串表示"):
            expected = f"{self.user.username} on {self.post.title}"
            self.assertEqual(str(self.comment), expected)

    @allure.story("评论回复")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试评论的回复功能")
    @pytest.mark.high
    def test_comment_reply(self):
        """测试评论回复"""
        with allure.step("创建回复评论"):
            reply = Comment.objects.create(
                post=self.post, author=self.user, content="Test Reply", parent=self.comment
            )
        
        with allure.step("验证回复关系"):
            self.assertEqual(reply.parent, self.comment)
            self.assertIn(reply, self.comment.replies.all())

    @allure.story("评论排序")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试评论按创建时间排序的功能")
    @pytest.mark.medium
    def test_comment_ordering(self):
        """测试评论排序"""
        with allure.step("创建测试数据"):
            with transaction.atomic():
                # 设置最早的评论时间
                old_time = timezone.now() - timedelta(hours=1)
                Comment.objects.filter(pk=self.comment.pk).update(created_at=old_time)

                # 创建新评论
                reply = Comment.objects.create(
                    post=self.post,
                    author=self.user,
                    content="Test Reply",
                    parent=self.comment,
                )

                # 刷新对象状态
                self.comment.refresh_from_db()
                reply.refresh_from_db()

        with allure.step("验证排序结果"):
            # 获取所有评论并验证排序
            comments = list(Comment.objects.all().order_by("-created_at"))
            self.assertEqual(comments[0].pk, reply.pk)  # 最新的评论应该在前
            self.assertEqual(comments[1].pk, self.comment.pk)  # 较早的评论应该在后
