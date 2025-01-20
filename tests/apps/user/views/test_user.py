import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

@pytest.fixture
def register_url():
    """返回注册URL"""
    return reverse('user:register')

@pytest.fixture
def profile_url():
    """返回用户资料URL"""
    return reverse('user:profile')

@pytest.mark.django_db
class TestUserView:
    """用户视图测试"""

    def test_user_register(self, api_client, register_url):
        """测试用户注册"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewTest123456',
            'password2': 'NewTest123456'
        }
        response = api_client.post(register_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 201
        assert 'id' in response.data['data']
        assert response.data['data']['username'] == 'newuser'
        assert User.objects.filter(username='newuser').exists()

    def test_user_register_duplicate_username(self, api_client, test_user, register_url):
        """测试用户注册-用户名重复"""
        data = {
            'username': test_user.username,
            'email': 'another@example.com',
            'password': 'Test123456',
            'password2': 'Test123456'
        }
        response = api_client.post(register_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] == 400
        assert 'username' in response.data['data']['errors']

    def test_user_register_duplicate_email(self, api_client, test_user, register_url):
        """测试用户注册-邮箱重复"""
        data = {
            'username': 'anotheruser',
            'email': test_user.email,
            'password': 'Test123456',
            'password2': 'Test123456'
        }
        response = api_client.post(register_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['code'] == 400
        assert 'email' in response.data['data']['errors']

    def test_get_user_profile(self, authenticated_client, profile_url, test_user):
        """测试获取用户资料"""
        response = authenticated_client.get(profile_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['username'] == test_user.username
        assert response.data['data']['email'] == test_user.email
        assert response.data['data']['nickname'] == test_user.nickname
        assert response.data['data']['bio'] == test_user.bio

    def test_get_user_profile_unauthenticated(self, api_client, profile_url):
        """测试未认证用户获取用户资料"""
        response = api_client.get(profile_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_profile(self, authenticated_client, profile_url):
        """测试更新用户资料"""
        data = {
            'nickname': 'Updated User',
            'bio': 'Updated bio'
        }
        response = authenticated_client.patch(profile_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['nickname'] == 'Updated User'
        assert response.data['data']['bio'] == 'Updated bio'

    def test_update_user_profile_unauthenticated(self, api_client, profile_url):
        """测试未认证用户更新用户资料"""
        data = {
            'nickname': 'Updated User',
            'bio': 'Updated bio'
        }
        response = api_client.patch(profile_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 