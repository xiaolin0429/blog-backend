import pytest
from django.urls import reverse
from rest_framework import status
from tests.apps.post.factories import PostFactory, UserFactory
from django.utils import timezone

@pytest.mark.django_db
class TestSearchView:
    def test_search_without_keyword(self, api_client):
        """测试没有关键词的搜索"""
        url = reverse('post:search')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert '搜索关键词不能为空' in response.data['message']

    def test_search_posts(self, api_client, user_factory, post_factory):
        """测试文章搜索"""
        # 创建测试用户和文章
        user = user_factory()
        post_factory(
            title='Python教程',
            content='这是一篇Python教程',
            excerpt='Python入门指南',
            author=user,
            status='published'
        )
        post_factory(
            title='Django教程',
            content='这是一篇Django教程',
            excerpt='Django入门指南',
            author=user,
            status='published'
        )
        
        url = reverse('post:search')
        response = api_client.get(f'{url}?keyword=Python')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['count'] == 1
        assert 'Python' in response.data['data']['results'][0]['title']

    def test_search_with_filters(self, api_client, user_factory, post_factory):
        """测试带过滤条件的搜索"""
        # 创建测试用户和文章
        user = user_factory()
        post = post_factory(
            title='Python教程',
            content='这是一篇Python教程',
            excerpt='Python入门指南',
            author=user,
            status='published'
        )
        
        url = reverse('post:search')
        response = api_client.get(
            f'{url}?keyword=Python&highlight=false'  # 禁用高亮
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['count'] == 1
        assert response.data['data']['results'][0]['title'] == 'Python教程'

    def test_search_with_date_range(self, api_client, user_factory, post_factory):
        """测试日期范围搜索"""
        # 创建测试用户和文章
        user = user_factory()
        current_date = timezone.now()
        post_factory(
            title='Python教程',
            content='这是一篇Python教程',
            author=user,
            status='published',
            created_at=current_date
        )
        
        # 使用当前日期作为范围
        start_date = current_date.date().isoformat()
        end_date = current_date.date().isoformat()
        
        url = reverse('post:search')
        response = api_client.get(
            f'{url}?keyword=Python&date_start={start_date}&date_end={end_date}'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['count'] == 1

    def test_search_with_highlight(self, api_client, user_factory, post_factory):
        """测试搜索结果高亮"""
        # 创建测试用户和文章
        user = user_factory()
        post_factory(
            title='Python教程',
            content='这是一篇Python教程',
            author=user,
            status='published'
        )
        
        url = reverse('post:search')
        response = api_client.get(f'{url}?keyword=Python&highlight=true')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert '<span class="search-highlight">Python</span>' in response.data['data']['results'][0]['title']


@pytest.mark.django_db
class TestSearchSuggestView:
    def test_suggest_without_keyword(self, api_client):
        """测试没有关键词的搜索建议"""
        url = reverse('post:search_suggest')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert '搜索关键词不能为空' in response.data['message']

    def test_suggest_posts(self, api_client, user_factory, post_factory):
        """测试文章搜索建议"""
        # 创建测试用户和文章
        user = user_factory()
        post_factory(
            title='Python教程',
            content='这是一篇Python教程',
            excerpt='Python入门指南',
            author=user,
            status='published'
        )
        
        url = reverse('post:search_suggest')
        response = api_client.get(f'{url}?keyword=Python')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert len(response.data['data']['suggestions']) > 0
        assert response.data['data']['suggestions'][0]['type'] == 'post'
        assert 'Python' in response.data['data']['suggestions'][0]['title']

    def test_suggest_categories_and_tags(self, api_client, post_factory):
        """测试分类和标签搜索建议"""
        # 创建带有Python相关分类和标签的文章
        post = post_factory(
            title='Python教程',
            status='published'
        )
        # 工厂会自动创建关联的分类和标签
        
        url = reverse('post:search_suggest')
        response = api_client.get(f'{url}?keyword=Python')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        suggestions = response.data['data']['suggestions']
        # 验证返回的建议中包含文章、分类或标签
        assert any(s['type'] in ['post', 'category', 'tag'] for s in suggestions)

    def test_suggest_limit(self, api_client, user_factory, post_factory):
        """测试搜索建议数量限制"""
        # 创建测试用户和多个文章
        user = user_factory()
        for i in range(15):
            post_factory(
                title=f'Python教程{i}',
                content=f'这是一篇Python教程{i}',
                author=user,
                status='published'
            )
        
        url = reverse('post:search_suggest')
        response = api_client.get(f'{url}?keyword=Python&limit=5')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert len(response.data['data']['suggestions']) == 5 