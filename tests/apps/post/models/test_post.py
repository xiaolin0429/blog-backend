from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.post.models import Category, Post, Tag


class PostModelTest(TestCase):
    """文章模型测试"""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.tag = Tag.objects.create(name="Test Tag")
        self.post = Post.objects.create(
            title="Test Post",
            content="Test Content",
            excerpt="Test Excerpt",
            author=self.user,
            category=self.category,
            status="draft",
        )
        self.post.tags.add(self.tag)

    def test_post_creation(self):
        """测试文章创建"""
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.content, "Test Content")
        self.assertEqual(self.post.excerpt, "Test Excerpt")
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.category, self.category)
        self.assertEqual(self.post.status, "draft")
        self.assertEqual(self.post.views, 0)
        self.assertEqual(self.post.likes, 0)
        self.assertIsNone(self.post.published_at)

    def test_post_str_representation(self):
        """测试文章字符串表示"""
        self.assertEqual(str(self.post), "Test Post")

    def test_post_tags(self):
        """测试文章标签"""
        self.assertEqual(self.post.tags.count(), 1)
        self.assertIn(self.tag, self.post.tags.all())

    def test_post_publish(self):
        """测试文章发布"""
        self.post.status = "published"
        self.post.save()
        self.assertIsNotNone(self.post.published_at)
        self.assertTrue(isinstance(self.post.published_at, timezone.datetime))

    def test_post_ordering(self):
        """测试文章排序"""
        # 设置第一篇文章的创建时间
        old_time = timezone.now() - timezone.timedelta(hours=1)
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

        # 获取所有文章并验证排序
        posts = Post.objects.all()
        self.assertEqual(posts[0], new_post)  # 最新的文章应该在前
        self.assertEqual(posts[1], self.post)  # 较早的文章应该在后
