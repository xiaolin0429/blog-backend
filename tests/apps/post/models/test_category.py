from django.db import IntegrityError
from django.test import TestCase

import allure
import pytest
from apps.post.models import Category


@allure.epic("文章管理")
@allure.feature("分类模型")
class CategoryModelTest(TestCase):
    """分类模型测试"""

    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category", description="Test Description"
        )

    @allure.story("分类创建")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试分类创建时各个字段的基本属性和默认值")
    @pytest.mark.high
    def test_category_creation(self):
        """测试分类创建"""
        with allure.step("验证分类属性"):
            self.assertEqual(self.category.name, "Test Category")
            self.assertEqual(self.category.description, "Test Description")
            self.assertIsNone(self.category.parent)
            self.assertEqual(self.category.order, 0)

    @allure.story("分类基础功能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试分类的字符串表示方法")
    @pytest.mark.medium
    def test_category_str_representation(self):
        """测试分类字符串表示"""
        with allure.step("验证分类字符串表示"):
            self.assertEqual(str(self.category), "Test Category")

    @allure.story("分类约束")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试分类名称的唯一性约束")
    @pytest.mark.high
    def test_category_unique_name(self):
        """测试分类名称唯一性"""
        with allure.step("尝试创建重复名称的分类"):
            with self.assertRaises(IntegrityError):
                Category.objects.create(name="Test Category")

    @allure.story("分类层级")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试分类的父子关系功能")
    @pytest.mark.high
    def test_category_parent_child_relationship(self):
        """测试分类父子关系"""
        with allure.step("创建子分类"):
            child_category = Category.objects.create(
                name="Child Category", description="Child Description", parent=self.category
            )
        
        with allure.step("验证父子关系"):
            self.assertEqual(child_category.parent, self.category)
            self.assertIn(child_category, self.category.children.all())
