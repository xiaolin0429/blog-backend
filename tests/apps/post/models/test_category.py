from django.db import IntegrityError
from django.test import TestCase

from apps.post.models import Category


class CategoryModelTest(TestCase):
    """分类模型测试"""

    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category", description="Test Description"
        )

    def test_category_creation(self):
        """测试分类创建"""
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.description, "Test Description")
        self.assertIsNone(self.category.parent)
        self.assertEqual(self.category.order, 0)

    def test_category_str_representation(self):
        """测试分类字符串表示"""
        self.assertEqual(str(self.category), "Test Category")

    def test_category_unique_name(self):
        """测试分类名称唯一性"""
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Test Category")

    def test_category_parent_child_relationship(self):
        """测试分类父子关系"""
        child_category = Category.objects.create(
            name="Child Category", description="Child Description", parent=self.category
        )
        self.assertEqual(child_category.parent, self.category)
        self.assertIn(child_category, self.category.children.all())
