import pytest
from django.urls import reverse
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware

@pytest.mark.django_db
class TestGlobalCommentAPI:
    """全局评论API测试"""

    def test_list_comments_anonymous(self, client):
        """测试匿名用户获取评论列表"""
        url = reverse('post:global_comment_list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'data' in data
        assert 'count' in data['data']
        assert 'results' in data['data']

    def test_list_comments_pagination(self, auth_client, comment_factory):
        """测试评论列表分页"""
        # 创建15条评论
        comment_factory.create_batch(15)
        
        url = reverse('post:global_comment_list')
        # 测试第一页
        response = auth_client.get(f"{url}?page=1&size=10")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['data']['results']) == 10
        
        # 测试第二页
        response = auth_client.get(f"{url}?page=2&size=10")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['data']['results']) == 5

    def test_list_comments_ordering(self, auth_client, comment_factory):
        """测试评论列表排序"""
        # 创建3条评论，间隔1小时
        now = timezone.now()
        for i in range(3):
            comment_factory.create(
                created_at=now - timedelta(hours=i)
            )
        
        url = reverse('post:global_comment_list')
        # 测试按创建时间降序
        response = auth_client.get(f"{url}?ordering=-created_at")
        assert response.status_code == status.HTTP_200_OK
        results = response.json()['data']['results']
        assert len(results) == 3
        # 验证排序
        created_times = [result['created_at'] for result in results]
        assert created_times == sorted(created_times, reverse=True)

    def test_filter_by_post(self, auth_client, comment_factory, post_factory):
        """测试按文章筛选评论"""
        post1 = post_factory.create()
        post2 = post_factory.create()
        # 为post1创建2条评论
        comment_factory.create_batch(2, post=post1)
        # 为post2创建1条评论
        comment_factory.create(post=post2)
        
        url = reverse('post:global_comment_list')
        response = auth_client.get(f"{url}?post={post1.id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['data']['results']) == 2

    def test_filter_by_author(self, auth_client, comment_factory, user_factory):
        """测试按作者筛选评论"""
        author1 = user_factory.create()
        author2 = user_factory.create()
        # 作者1发表2条评论
        comment_factory.create_batch(2, author=author1)
        # 作者2发表1条评论
        comment_factory.create(author=author2)
        
        url = reverse('post:global_comment_list')
        response = auth_client.get(f"{url}?author={author1.id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['data']['results']) == 2

    def test_filter_by_date_range(self, auth_client, comment_factory):
        """测试按日期范围筛选评论"""
        # 使用固定的日期时间
        day1 = make_aware(datetime(2024, 1, 1, 12, 0))  # 1月1日中午
        day2 = make_aware(datetime(2024, 1, 2, 12, 0))  # 1月2日中午
        day3 = make_aware(datetime(2024, 1, 3, 12, 0))  # 1月3日中午
        
        # 创建3条评论，分别在不同日期
        comment_factory.create(created_at=day1)  # 1月1日的评论
        comment_factory.create(created_at=day2)  # 1月2日的评论
        comment_factory.create(created_at=day3)  # 1月3日的评论
        
        url = reverse('post:global_comment_list')
        
        # 测试开始日期筛选（1月2日及以后的评论）
        response = auth_client.get(f"{url}?start_date=2024-01-02")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['data']['results']) == 2
        
        # 测试结束日期筛选（1月2日及以前的评论）
        response = auth_client.get(f"{url}?end_date=2024-01-02")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['data']['results']) == 2
        
        # 测试日期范围筛选（只看1月2日的评论）
        response = auth_client.get(f"{url}?start_date=2024-01-02&end_date=2024-01-02")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['data']['results']) == 1

    def test_search_by_keyword(self, auth_client, comment_factory, user_factory):
        """测试关键词搜索"""
        author = user_factory.create(username="testuser")
        # 创建包含特定关键词的评论
        comment_factory.create(content="测试评论内容", author=author)
        # 创建其他评论
        comment_factory.create(content="普通评论")
        
        url = reverse('post:global_comment_list')
        # 测试按内容搜索
        response = auth_client.get(f"{url}?keyword=测试")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['data']['results']) == 1
        
        # 测试按用户名搜索
        response = auth_client.get(f"{url}?keyword=testuser")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()['data']['results']) == 1 