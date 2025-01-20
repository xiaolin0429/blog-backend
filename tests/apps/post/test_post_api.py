from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.post.models import Post
from tests.apps.post.factories import PostFactory


class PostAPITests(APITestCase):
    def setUp(self):
        """测试前的初始化工作"""
        self.post = PostFactory()
        self.list_url = reverse('post-list')
        self.detail_url = reverse('post-detail', args=[self.post.id])

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
            'title': 'Test Post',
            'content': 'Test Content',
            'status': Post.Status.PUBLISHED
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.data['title'], 'Test Post') 