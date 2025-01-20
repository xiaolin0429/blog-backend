import pytest
from django.urls import reverse
from rest_framework import status
from apps.post.models import Comment

pytestmark = pytest.mark.django_db

class TestCommentAPI:
    """评论API测试"""

    def test_list_comments(self, client, post, user):
        """测试获取评论列表"""
        # 创建一些测试评论
        Comment.objects.create(post=post, author=user, content="测试评论1")
        Comment.objects.create(post=post, author=user, content="测试评论2")
        
        url = reverse('post:comment_list_create', kwargs={'post_id': post.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 2
        assert response.data['data'][0]['content'] == "测试评论1"

    def test_create_comment(self, auth_client, post, user):
        """测试创建评论"""
        url = reverse('post:comment_list_create', kwargs={'post_id': post.id})
        data = {'content': '新评论'}
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['content'] == '新评论'
        assert response.data['data']['author']['id'] == user.id
        assert Comment.objects.count() == 1

    def test_create_comment_with_invalid_post(self, auth_client):
        """测试对不存在的文章创建评论"""
        url = reverse('post:comment_list_create', kwargs={'post_id': 99999})
        data = {'content': '新评论'}
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Comment.objects.count() == 0

    def test_create_reply(self, auth_client, post, user, comment):
        """测试创建评论回复"""
        url = reverse('post:comment_list_create', kwargs={'post_id': post.id})
        data = {
            'content': '回复评论',
            'parent': comment.id
        }
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['parent'] == comment.id
        assert Comment.objects.count() == 2

    def test_create_nested_reply(self, auth_client, post, user, reply):
        """测试创建嵌套回复（不允许）"""
        url = reverse('post:comment_list_create', kwargs={'post_id': post.id})
        data = {
            'content': '嵌套回复',
            'parent': reply.id
        }
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '不能回复回复' in str(response.data)

    def test_create_cross_post_reply(self, auth_client, post, other_post, comment):
        """测试跨文章回复（不允许）"""
        url = reverse('post:comment_list_create', kwargs={'post_id': other_post.id})
        data = {
            'content': '跨文章回复',
            'parent': comment.id
        }
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '不能回复其他文章的评论' in str(response.data)

    def test_update_comment(self, auth_client, comment):
        """测试更新评论"""
        url = reverse('post:comment_detail', kwargs={'pk': comment.id})
        data = {'content': '更新后的评论'}
        response = auth_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['content'] == '更新后的评论'
        comment.refresh_from_db()
        assert comment.content == '更新后的评论'

    def test_update_other_user_comment(self, other_auth_client, comment):
        """测试更新其他用户的评论（不允许）"""
        url = reverse('post:comment_detail', kwargs={'pk': comment.id})
        data = {'content': '尝试更新他人的评论'}
        response = other_auth_client.put(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        comment.refresh_from_db()
        assert comment.content != '尝试更新他人的评论'

    def test_delete_comment(self, auth_client, comment):
        """测试删除评论"""
        url = reverse('post:comment_detail', kwargs={'pk': comment.id})
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(id=comment.id).exists()

    def test_delete_other_user_comment(self, other_auth_client, comment):
        """测试删除其他用户的评论（不允许）"""
        url = reverse('post:comment_detail', kwargs={'pk': comment.id})
        response = other_auth_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.filter(id=comment.id).exists()

    def test_anonymous_user_operations(self, client, post, comment):
        """测试未登录用户的操作限制"""
        # 测试创建评论
        create_url = reverse('post:comment_list_create', kwargs={'post_id': post.id})
        create_response = client.post(create_url, {'content': '匿名评论'})
        assert create_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # 测试更新评论
        update_url = reverse('post:comment_detail', kwargs={'pk': comment.id})
        update_response = client.put(update_url, {'content': '更新评论'})
        assert update_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # 测试删除评论
        delete_response = client.delete(update_url)
        assert delete_response.status_code == status.HTTP_401_UNAUTHORIZED 