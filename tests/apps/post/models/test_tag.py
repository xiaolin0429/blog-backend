from django.db import IntegrityError
from django.test import TestCase

from apps.post.models import Tag


class TagModelTest(TestCase):
    """标签模型测试"""

    def setUp(self):
        self.tag = Tag.objects.create(name="Test Tag", description="Test Description")

    def test_tag_creation(self):
        """测试标签创建"""
        self.assertEqual(self.tag.name, "Test Tag")
        self.assertEqual(self.tag.description, "Test Description")

    def test_tag_str_representation(self):
        """测试标签字符串表示"""
        self.assertEqual(str(self.tag), "Test Tag")

    def test_tag_unique_name(self):
        """测试标签名称唯一性"""
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Test Tag")
