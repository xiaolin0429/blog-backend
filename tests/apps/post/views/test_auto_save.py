import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import allure
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.post.models import Post

User = get_user_model()


@allure.epic("文章管理")
@allure.feature("文章自动保存")
class PostAutoSaveTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(
            title="Test Post", content="Test Content", author=self.user
        )
        self.client.force_authenticate(user=self.user)
        self.auto_save_url = reverse("post:post_auto_save", args=[self.post.id])

    @allure.story("自动保存功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试文章自动保存功能的基本操作，包括保存标题、内容和摘要")
    @pytest.mark.high
    def test_auto_save_post(self):
        """测试自动保存文章"""
        with allure.step("准备测试数据"):
            data = {
                "title": "Updated Title",
                "content": "Updated Content",
                "excerpt": "Updated Excerpt",
            }
        
        with allure.step("发送自动保存请求"):
            response = self.client.post(self.auto_save_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with allure.step("验证自动保存内容"):
            post = Post.objects.get(id=self.post.id)
            auto_save_content = post.auto_save_content
            self.assertEqual(auto_save_content["title"], "Updated Title")
            self.assertEqual(auto_save_content["content"], "Updated Content")
            self.assertEqual(auto_save_content["excerpt"], "Updated Excerpt")

    @allure.story("自动保存功能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试获取已自动保存的文章内容")
    @pytest.mark.medium
    def test_get_auto_save_content(self):
        """测试获取自动保存的内容"""
        with allure.step("先保存一些内容"):
            data = {
                "title": "Auto Saved Title",
                "content": "Auto Saved Content",
                "excerpt": "Auto Saved Excerpt",
            }
            self.client.post(self.auto_save_url, data, format="json")

        with allure.step("获取自动保存的内容"):
            response = self.client.get(self.auto_save_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with allure.step("验证返回的内容"):
            content = json.loads(response.content)
            self.assertEqual(content["data"]["title"], "Auto Saved Title")
            self.assertEqual(content["data"]["content"], "Auto Saved Content")
            self.assertEqual(content["data"]["excerpt"], "Auto Saved Excerpt")

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("测试未登录用户无法使用自动保存功能")
    @pytest.mark.security
    def test_auto_save_unauthorized(self):
        """测试未授权用户无法自动保存"""
        with allure.step("移除用户认证"):
            self.client.force_authenticate(user=None)
        
        with allure.step("尝试自动保存"):
            response = self.client.post(self.auto_save_url, {}, format="json")
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试用户无法自动保存其他用户的文章")
    @pytest.mark.security
    def test_auto_save_wrong_user(self):
        """测试其他用户无法自动保存他人的文章"""
        with allure.step("创建另一个用户"):
            other_user = User.objects.create_user(
                username="otheruser", email="other@example.com", password="otherpass123"
            )
            self.client.force_authenticate(user=other_user)

        with allure.step("尝试保存其他用户的文章"):
            data = {
                "title": "Updated Title",
                "content": "Updated Content",
                "excerpt": "Updated Excerpt",
            }
            response = self.client.post(self.auto_save_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @allure.story("频率限制")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试自动保存的频率限制功能")
    @pytest.mark.performance
    def test_auto_save_rate_limit(self):
        """测试自动保存的频率限制"""
        with allure.step("第一次保存"):
            data = {
                "title": "First Save",
                "content": "First Content",
                "excerpt": "First Excerpt",
            }
            response = self.client.post(self.auto_save_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with allure.step("立即尝试第二次保存"):
            data = {
                "title": "Second Save",
                "content": "Second Content",
                "excerpt": "Second Excerpt",
            }
            response = self.client.post(self.auto_save_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        with allure.step("使用force_save参数强制保存"):
            data["force_save"] = True
            response = self.client.post(self.auto_save_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @allure.story("自动保存功能")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("测试自动保存返回的下次保存时间信息")
    @pytest.mark.low
    def test_auto_save_next_save_time(self):
        """测试自动保存返回下次保存时间"""
        with allure.step("发送自动保存请求"):
            data = {
                "title": "Test Save",
                "content": "Test Content",
                "excerpt": "Test Excerpt",
            }
            response = self.client.post(self.auto_save_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        with allure.step("验证返回的时间信息"):
            response_data = response.json()["data"]
            self.assertIn("next_save_time", response_data)
            self.assertIn("version", response_data) 