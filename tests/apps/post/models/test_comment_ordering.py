from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase
from django.utils import timezone

import allure
import pytest
from apps.post.models import Comment, Post

User = get_user_model()


@allure.epic("评论管理")
@allure.feature("评论排序")
class CommentOrderingTest(TestCase):
    def setUp(self):
        """测试数据初始化"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(
            title="Test Post", content="Test Content", author=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post, author=self.user, content="Test Comment"
        )

    @allure.story("基本排序")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试评论按创建时间排序的基本功能")
    @pytest.mark.high
    def test_comment_ordering(self):
        """测试评论排序"""
        with allure.step("创建测试数据"):
            with transaction.atomic():
                # 设置最早的评论时间
                old_time = timezone.now() - timedelta(hours=1)
                Comment.objects.filter(pk=self.comment.pk).update(created_at=old_time)

                # 创建新评论
                new_comment = Comment.objects.create(
                    post=self.post, author=self.user, content="New Comment"
                )

                # 刷新对象状态
                self.comment.refresh_from_db()
                new_comment.refresh_from_db()

        with allure.step("验证排序结果"):
            # 获取所有评论并验证排序
            comments = list(Comment.objects.all().order_by("-created_at"))
            self.assertEqual(comments[0].pk, new_comment.pk)  # 最新的评论应该在前
            self.assertEqual(comments[1].pk, self.comment.pk)  # 较早的评论应该在后

    @allure.story("回复排序")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试评论回复的时间排序功能")
    @pytest.mark.high
    def test_comment_reply_ordering(self):
        """测试评论回复排序"""
        with allure.step("创建测试数据"):
            with transaction.atomic():
                # 设置最早的评论时间
                old_time = timezone.now() - timedelta(hours=1)
                Comment.objects.filter(pk=self.comment.pk).update(created_at=old_time)

                # 创建回复评论
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
