import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.post.models import Post

User = get_user_model()


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

    def test_auto_save_post(self):
        """测试自动保存文章"""
        data = {
            "title": "Updated Title",
            "content": "Updated Content",
            "excerpt": "Updated Excerpt",
        }
        response = self.client.post(self.auto_save_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 验证自动保存内容
        post = Post.objects.get(id=self.post.id)
        auto_save_content = post.auto_save_content
        self.assertEqual(auto_save_content["title"], "Updated Title")
        self.assertEqual(auto_save_content["content"], "Updated Content")
        self.assertEqual(auto_save_content["excerpt"], "Updated Excerpt")

    def test_get_auto_save_content(self):
        """测试获取自动保存的内容"""
        # 先保存一些内容
        data = {
            "title": "Auto Saved Title",
            "content": "Auto Saved Content",
            "excerpt": "Auto Saved Excerpt",
        }
        self.client.post(self.auto_save_url, data, format="json")

        # 获取自动保存的内容
        response = self.client.get(self.auto_save_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content)
        self.assertEqual(content["data"]["title"], "Auto Saved Title")
        self.assertEqual(content["data"]["content"], "Auto Saved Content")
        self.assertEqual(content["data"]["excerpt"], "Auto Saved Excerpt")

    def test_auto_save_unauthorized(self):
        """测试未授权用户无法自动保存"""
        self.client.force_authenticate(user=None)
        response = self.client.post(self.auto_save_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auto_save_wrong_user(self):
        """测试其他用户无法自动保存他人的文章"""
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )
        self.client.force_authenticate(user=other_user)
        data = {
            "title": "Updated Title",
            "content": "Updated Content",
            "excerpt": "Updated Excerpt",
        }
        response = self.client.post(self.auto_save_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_auto_save_rate_limit(self):
        """测试自动保存的频率限制"""
        # 第一次保存
        data = {
            "title": "First Save",
            "content": "First Content",
            "excerpt": "First Excerpt",
        }
        response = self.client.post(self.auto_save_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 立即再次保存，应该被限制
        data = {
            "title": "Second Save",
            "content": "Second Content",
            "excerpt": "Second Excerpt",
        }
        response = self.client.post(self.auto_save_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

        # 使用force_save参数强制保存
        data["force_save"] = True
        response = self.client.post(self.auto_save_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auto_save_next_save_time(self):
        """测试自动保存返回下次保存时间"""
        data = {
            "title": "Test Save",
            "content": "Test Content",
            "excerpt": "Test Excerpt",
        }
        response = self.client.post(self.auto_save_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertIn("next_save_time", response_data)
        self.assertIn("version", response_data)
