from django.db import IntegrityError
from django.test import TestCase

import allure
import pytest
from apps.post.models import Tag


@allure.epic("文章管理")
@allure.feature("标签模型")
class TagModelTest(TestCase):
    """标签模型测试"""

    def setUp(self):
        self.tag = Tag.objects.create(name="Test Tag", description="Test Description")

    @allure.story("标签创建")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试标签创建时各个字段的基本属性")
    @pytest.mark.high
    def test_tag_creation(self):
        """测试标签创建"""
        with allure.step("验证标签属性"):
            self.assertEqual(self.tag.name, "Test Tag")
            self.assertEqual(self.tag.description, "Test Description")

    @allure.story("标签基础功能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试标签的字符串表示方法")
    @pytest.mark.medium
    def test_tag_str_representation(self):
        """测试标签字符串表示"""
        with allure.step("验证标签字符串表示"):
            self.assertEqual(str(self.tag), "Test Tag")

    @allure.story("标签约束")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试标签名称的唯一性约束")
    @pytest.mark.high
    def test_tag_unique_name(self):
        """测试标签名称唯一性"""
        with allure.step("尝试创建重复名称的标签"):
            with self.assertRaises(IntegrityError):
                Tag.objects.create(name="Test Tag")
