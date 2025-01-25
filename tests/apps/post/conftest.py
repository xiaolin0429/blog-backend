import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.post.models import Comment, Post, Tag
from apps.user.models import User

User = get_user_model()


@pytest.fixture
def user(db):
    """创建测试用户"""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def other_user(db):
    """创建另一个测试用户"""
    return User.objects.create_user(
        username="otheruser", email="other@example.com", password="testpass123"
    )


@pytest.fixture
def auth_client(user):
    """创建已认证的测试客户端"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def other_auth_client(other_user):
    """创建另一个已认证的测试客户端"""
    client = APIClient()
    client.force_authenticate(user=other_user)
    return client


@pytest.fixture
def post(user):
    """创建测试文章"""
    return Post.objects.create(title="测试文章", content="测试内容", author=user)


@pytest.fixture
def other_post(other_user):
    """创建另一个测试文章"""
    return Post.objects.create(title="另一篇测试文章", content="另一篇测试内容", author=other_user)


@pytest.fixture
def comment(post, user):
    """创建测试评论"""
    return Comment.objects.create(post=post, author=user, content="测试评论")


@pytest.fixture
def reply(post, other_user, comment):
    """创建测试回复"""
    return Comment.objects.create(
        post=post, author=other_user, content="测试回复", parent=comment
    )


@pytest.fixture
def other_user_comment(other_user, post):
    """创建其他用户的评论"""
    return Comment.objects.create(
        content="Test comment by other user", author=other_user, post=post
    )


@pytest.fixture
def tag(db):
    """创建测试标签"""
    return Tag.objects.create(name="Test Tag", description="Test Description")
