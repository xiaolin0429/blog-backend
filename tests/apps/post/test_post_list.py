import pytest
from django.urls import reverse
from rest_framework import status
from apps.post.models import Post, Category, Tag

@pytest.mark.django_db
class TestPostListView:
    def test_get_post_list_as_anonymous(self, api_client):
        """测试匿名用户只能看到已发布的文章"""
        url = reverse('post:post_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0

    def test_get_post_list_as_normal_user(self, normal_user, api_client):
        """测试普通用户只能看到已发布的文章"""
        # 创建一篇已发布的文章
        Post.objects.create(
            title='已发布文章',
            content='内容',
            author=normal_user,
            status='published'
        )
        
        # 创建一篇草稿
        Post.objects.create(
            title='草稿文章',
            content='内容',
            author=normal_user,
            status='draft'
        )
        
        api_client.force_authenticate(user=normal_user)
        url = reverse('post:post_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1  # 总数为1
        assert len(response.data['results']) == 1  # 结果列表长度为1
        assert response.data['results'][0]['title'] == '已发布文章'

    def test_get_post_list_as_admin(self, admin_user, api_client):
        """测试管理员可以看到所有文章"""
        # 创建三篇不同状态的文章
        Post.objects.create(
            title='已发布文章',
            content='内容',
            author=admin_user,
            status='published'
        )
        Post.objects.create(
            title='草稿文章',
            content='内容',
            author=admin_user,
            status='draft'
        )
        Post.objects.create(
            title='已归档文章',
            content='内容',
            author=admin_user,
            status='archived'
        )
        
        api_client.force_authenticate(user=admin_user)
        url = reverse('post:post_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3  # 总数为3
        assert len(response.data['results']) == 3  # 结果列表长度为3

    def test_filter_posts_by_category(self, normal_user, api_client):
        """测试按分类筛选文章"""
        # 创建两个分类
        category1 = Category.objects.create(name='分类1')
        category2 = Category.objects.create(name='分类2')
        
        # 创建两篇文章,分别属于不同分类
        Post.objects.create(
            title='文章1',
            content='内容1',
            author=normal_user,
            category=category1,
            status='published'
        )
        Post.objects.create(
            title='文章2',
            content='内容2',
            author=normal_user,
            category=category2,
            status='published'
        )
        
        api_client.force_authenticate(user=normal_user)
        url = reverse('post:post_list')
        response = api_client.get(f'{url}?category={category1.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1  # 总数为1
        assert len(response.data['results']) == 1  # 结果列表长度为1
        assert response.data['results'][0]['category'] == category1.id

    def test_filter_posts_by_tags(self, normal_user, api_client):
        """测试按标签筛选文章"""
        # 创建两个标签
        tag1 = Tag.objects.create(name='标签1')
        tag2 = Tag.objects.create(name='标签2')
        
        # 创建两篇文章,分别添加不同标签
        post1 = Post.objects.create(
            title='文章1',
            content='内容1',
            author=normal_user,
            status='published'
        )
        post1.tags.add(tag1)
        
        post2 = Post.objects.create(
            title='文章2',
            content='内容2',
            author=normal_user,
            status='published'
        )
        post2.tags.add(tag2)
        
        api_client.force_authenticate(user=normal_user)
        url = reverse('post:post_list')
        response = api_client.get(f'{url}?tags={tag1.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1  # 总数为1
        assert len(response.data['results']) == 1  # 结果列表长度为1
        assert response.data['results'][0]['title'] == '文章1'

    def test_search_posts(self, normal_user, api_client):
        """测试搜索文章"""
        # 创建两篇包含Python的文章
        Post.objects.create(
            title='Python教程',
            content='Python入门指南',
            author=normal_user,
            status='published'
        )
        Post.objects.create(
            title='Django教程',
            content='Django入门指南',
            author=normal_user,
            status='published'
        )
        
        api_client.force_authenticate(user=normal_user)
        url = reverse('post:post_list')
        response = api_client.get(f'{url}?search=Python')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1  # 总数为1
        assert len(response.data['results']) == 1  # 结果列表长度为1
        assert 'Python' in response.data['results'][0]['title']

    def test_order_posts(self, normal_user, api_client):
        """测试文章排序"""
        # 创建两篇文章
        Post.objects.create(
            title='文章1',
            content='内容1',
            author=normal_user,
            views=10,
            likes=5,
            status='published'
        )
        Post.objects.create(
            title='文章2',
            content='内容2',
            author=normal_user,
            views=20,
            likes=15,
            status='published'
        )
        
        api_client.force_authenticate(user=normal_user)
        url = reverse('post:post_list')
        
        # 按浏览量排序
        response = api_client.get(f'{url}?ordering=-views')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['title'] == '文章2'
        
        # 按点赞数排序
        response = api_client.get(f'{url}?ordering=-likes')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['title'] == '文章2' 