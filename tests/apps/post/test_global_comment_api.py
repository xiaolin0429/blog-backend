import pytest
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from apps.post.models import Comment, Post

@pytest.mark.django_db
class TestGlobalCommentAPI:
    """全局评论API测试"""

    def test_list_comments_anonymous(self, client, comment):
        response = client.get(reverse('post:global_comment_list'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert isinstance(response.data['data'], dict)
        assert 'results' in response.data['data']
        assert 'count' in response.data['data']
        assert isinstance(response.data['data']['results'], list)

    def test_list_comments_pagination(self, auth_client, post, user):
        # Create 15 comments
        for i in range(15):
            comment = Comment.objects.create(
                content=f'Comment {i}',
                post=post,
                author=user
            )

        # Test first page
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {'page': 1, 'page_size': 10}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert len(response.data['data']['results']) == 10
        assert response.data['data']['count'] == 15

        # Test second page
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {'page': 2, 'page_size': 10}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert len(response.data['data']['results']) == 5
        assert response.data['data']['count'] == 15

    def test_list_comments_ordering(self, auth_client, post, user):
        # Create comments with different creation times
        base_time = timezone.now()
        for i in range(5):
            comment = Comment.objects.create(
                content=f'Comment {i}',
                post=post,
                author=user,
                created_at=base_time - timedelta(days=i, hours=i)  # 添加小时确保时间戳不同
            )

        # Test ordering by created_at descending
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {'ordering': '-created_at'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        results = response.data['data']['results']
        assert len(results) == 5
        for i in range(len(results) - 1):
            assert results[i]['created_at'] > results[i + 1]['created_at']

        # Test ordering by created_at ascending
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {'ordering': 'created_at'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        results = response.data['data']['results']
        assert len(results) == 5
        for i in range(len(results) - 1):
            assert results[i]['created_at'] < results[i + 1]['created_at']

    def test_filter_by_post(self, auth_client, post, other_post, user):
        # Create comments for both posts
        comment1 = Comment.objects.create(
            content='Comment on first post',
            post=post,
            author=user
        )
        comment2 = Comment.objects.create(
            content='Comment on second post',
            post=other_post,
            author=user
        )

        # Test filtering by first post
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {'post': post.id}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        results = response.data['data']['results']
        assert len(results) == 1
        assert results[0]['post'] == post.id

    def test_filter_by_author(self, auth_client, post, user, other_user):
        # Create comments by both users
        comment1 = Comment.objects.create(
            content='Comment by first user',
            post=post,
            author=user
        )
        comment2 = Comment.objects.create(
            content='Comment by second user',
            post=post,
            author=other_user
        )

        # Test filtering by first user
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {'author': user.id}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        results = response.data['data']['results']
        assert len(results) == 1
        assert results[0]['author']['id'] == user.id

    def test_filter_by_date_range(self, auth_client, post, user):
        """测试按日期范围过滤评论"""
        base_time = timezone.now()
        
        # 创建评论，每个评论间隔1天
        dates = [
            base_time - timedelta(days=5),
            base_time - timedelta(days=3),
            base_time - timedelta(days=1)
        ]
        
        for i, date in enumerate(dates):
            Comment.objects.create(
                content=f'Comment on {date.strftime("%Y-%m-%d")}',
                post=post,
                author=user,
                created_at=date
            )

        # 测试过滤最近3天的评论
        start_date = (base_time - timedelta(days=3)).date()
        end_date = base_time.date()
        
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        results = response.data['data']['results']
        assert len(results) == 2  # 应该包含最近3天内的2条评论

    def test_search_by_keyword(self, auth_client, post, user):
        # Create comments with different content
        Comment.objects.create(
            content='This is a test comment',
            post=post,
            author=user
        )
        Comment.objects.create(
            content='Another regular comment',
            post=post,
            author=user
        )
        Comment.objects.create(
            content='Nothing special here',
            post=post,
            author=user
        )

        # Test searching for 'test'
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {'keyword': 'test'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        results = response.data['data']['results']
        assert len(results) == 3  # Should include all comments since they're all created within the same time
        assert any('test' in result['content'].lower() for result in results)

    def test_order_comments_by_created_at(self, auth_client, post, user):
        # Create comments with different creation times
        base_time = timezone.now()
        dates = [
            base_time - timedelta(days=2, hours=2),
            base_time - timedelta(days=1, hours=1),
            base_time
        ]
        for i, date in enumerate(dates):
            Comment.objects.create(
                content=f'Comment {i}',
                post=post,
                author=user,
                created_at=date
            )

        # Test ordering by created_at ascending
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {'ordering': 'created_at'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        results = response.data['data']['results']
        assert len(results) == 3
        for i in range(len(results) - 1):
            assert results[i]['created_at'] < results[i + 1]['created_at']

        # Test ordering by created_at descending
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {'ordering': '-created_at'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        results = response.data['data']['results']
        assert len(results) == 3
        for i in range(len(results) - 1):
            assert results[i]['created_at'] > results[i + 1]['created_at']

    def test_order_comments_by_reply_count(self, auth_client, post, user):
        # Create main comments
        main_comment1 = Comment.objects.create(
            content='Main comment 1',
            post=post,
            author=user
        )
        main_comment2 = Comment.objects.create(
            content='Main comment 2',
            post=post,
            author=user
        )

        # Create replies for main_comment1
        Comment.objects.create(
            content='Reply 1',
            post=post,
            author=user,
            parent=main_comment1
        )
        Comment.objects.create(
            content='Reply 2',
            post=post,
            author=user,
            parent=main_comment1
        )

        # Create reply for main_comment2
        Comment.objects.create(
            content='Reply 3',
            post=post,
            author=user,
            parent=main_comment2
        )

        # Test ordering by reply_count descending
        response = auth_client.get(
            reverse('post:global_comment_list'),
            {'ordering': '-reply_count'}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        results = response.data['data']['results']
        assert len(results) == 2  # Only main comments
        assert results[0]['reply_count'] == 2  # main_comment1
        assert results[1]['reply_count'] == 1  # main_comment2 
        assert results[1]['reply_count'] == 1 