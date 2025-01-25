from django.contrib.auth import get_user_model

import pytest
from rest_framework.test import APIClient

from tests.apps.post.factories import CommentFactory, PostFactory, UserFactory

User = get_user_model()


@pytest.fixture
def normal_user(db):
    """创建普通用户"""
    return User.objects.create_user(
        username="normal_user",
        email="normal@example.com",
        password="testpass123",
        nickname="普通用户",
    )


@pytest.fixture
def admin_user(db):
    """创建管理员用户"""
    return User.objects.create_superuser(
        username="admin_user",
        email="admin@example.com",
        password="testpass123",
        nickname="管理员",
    )


@pytest.fixture
def api_client():
    """创建 API 测试客户端"""
    return APIClient()


@pytest.fixture
def user_data():
    """返回测试用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123456",
        "nickname": "Test User",
        "bio": "Test bio",
    }


@pytest.fixture
def test_user(user_data):
    """创建并返回测试用户"""
    return User.objects.create_user(**user_data)


@pytest.fixture
def authenticated_client(api_client, test_user):
    """返回已认证的API测试客户端"""
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def client():
    """返回API测试客户端"""
    return APIClient()


@pytest.fixture
def user():
    """创建测试用户"""
    return UserFactory()


@pytest.fixture
def auth_client(api_client, normal_user):
    """创建已认证的 API 测试客户端"""
    api_client.force_authenticate(user=normal_user)
    return api_client


@pytest.fixture
def user_factory():
    """返回用户工厂类"""
    return UserFactory


@pytest.fixture
def post_factory():
    """返回文章工厂类"""
    return PostFactory


@pytest.fixture
def comment_factory():
    """返回评论工厂类"""
    return CommentFactory


@pytest.fixture
def post(user):
    """创建测试文章"""
    return PostFactory(author=user, status="published")


@pytest.fixture
def other_user():
    """创建另一个测试用户"""
    return UserFactory()


@pytest.fixture
def other_post(other_user):
    """创建另一个测试文章"""
    return PostFactory(author=other_user, status="published")
