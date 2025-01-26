from django.contrib.auth import get_user_model
from django.urls import reverse

import allure
import pytest
from rest_framework import status
from rest_framework.test import APITestCase

from apps.post.models import Post
from tests.apps.post.factories import PostFactory

User = get_user_model()


@allure.epic("文章管理")
@allure.feature("文章API")
class PostAPITests(APITestCase):
    def setUp(self):
        """测试前的初始化工作"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.post = PostFactory(author=self.user, status="published")  # 设置为已发布状态
        self.list_url = "/api/v1/posts/"
        self.detail_url = f"/api/v1/posts/{self.post.id}/"

    @allure.story("文章列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试获取文章列表的基本功能")
    @pytest.mark.high
    def test_list_posts(self):
        """测试获取文章列表"""
        with allure.step("发送获取文章列表请求"):
            response = self.client.get(self.list_url)
        
        with allure.step("验证响应结果"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data["data"]["results"]), 1)

    @allure.story("文章详情")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试获取单个文章详情的功能")
    @pytest.mark.high
    def test_retrieve_post(self):
        """测试获取单个文章详情"""
        with allure.step("发送获取文章详情请求"):
            response = self.client.get(self.detail_url)
        
        with allure.step("验证响应结果"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["data"]["id"], self.post.id)

    @allure.story("创建文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试创建新文章的功能")
    @pytest.mark.high
    def test_create_post(self):
        """测试创建新文章"""
        with allure.step("准备创建文章数据"):
            data = {"title": "测试文章", "content": "测试内容", "status": "published"}
        
        with allure.step("发送创建文章请求"):
            response = self.client.post(self.list_url, data)
        
        with allure.step("验证响应结果"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["code"], 200)
            self.assertEqual(Post.objects.count(), 2)
            self.assertEqual(response.data["data"]["title"], "测试文章")
