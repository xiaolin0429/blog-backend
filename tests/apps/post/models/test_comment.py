from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TestCase
from django.utils import timezone

from apps.post.models import Category, Comment, Post


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

    def test_comment_creation(self):
        """测试评论创建"""
        self.assertEqual(self.comment.content, "Test Comment")
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.post, self.post)
        self.assertIsNone(self.comment.parent)

    def test_comment_str_representation(self):
        """测试评论字符串表示"""
        expected = f"{self.user.username} on {self.post.title}"
        self.assertEqual(str(self.comment), expected)

    def test_comment_reply(self):
        """测试评论回复"""
        reply = Comment.objects.create(
            post=self.post, author=self.user, content="Test Reply", parent=self.comment
        )
        self.assertEqual(reply.parent, self.comment)
        self.assertIn(reply, self.comment.replies.all())

    def test_comment_ordering(self):
        """测试评论排序"""
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

            # 获取所有评论并验证排序
            comments = list(Comment.objects.all().order_by("-created_at"))
            self.assertEqual(comments[0].pk, reply.pk)  # 最新的评论应该在前
            self.assertEqual(comments[1].pk, self.comment.pk)  # 较早的评论应该在后
