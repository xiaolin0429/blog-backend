from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.post.models import Post
from tests.apps.post.factories import PostFactory

User = get_user_model()

class PostAPITests(APITestCase):
    def setUp(self):
        """测试前的初始化工作"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.post = PostFactory(author=self.user)
        self.list_url = '/api/v1/posts/'
        self.detail_url = f'/api/v1/posts/{self.post.id}/'

    def test_list_posts(self):
        """测试获取文章列表"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_post(self):
        """测试获取单个文章详情"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.post.id)

    def test_create_post(self):
        """测试创建新文章"""
        data = {
            'title': '测试文章',
            'content': '测试内容',
            'status': 'published'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.data['title'], '测试文章') 