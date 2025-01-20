import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from tests.apps.post.factories import UserFactory, PostFactory, CommentFactory

User = get_user_model()

@pytest.fixture
def api_client():
    """返回API测试客户端"""
    return APIClient()

@pytest.fixture
def user_data():
    """返回测试用户数据"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123456',
        'nickname': 'Test User',
        'bio': 'Test bio'
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
def auth_client(user):
    """返回已认证的API测试客户端"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client

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