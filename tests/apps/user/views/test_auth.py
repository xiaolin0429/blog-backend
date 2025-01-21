import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

@pytest.fixture
def login_url():
    """返回登录URL"""
    return '/api/v1/auth/login/'

@pytest.fixture
def refresh_url():
    """返回刷新令牌URL"""
    return '/api/v1/auth/refresh/'

@pytest.fixture
def logout_url():
    """返回登出URL"""
    return '/api/v1/auth/logout/'

@pytest.fixture
def change_password_url():
    """返回修改密码URL"""
    return '/api/v1/user/me/password/'

@pytest.mark.django_db
class TestAuthView:
    """认证视图测试"""

    def test_user_login(self, api_client, test_user, login_url, user_data):
        """测试用户登录"""
        response = api_client.post(login_url, user_data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']

    def test_user_login_invalid_credentials(self, api_client, login_url):
        """测试用户登录失败"""
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, test_user, login_url, refresh_url, user_data):
        """测试刷新令牌"""
        # 先登录获取刷新令牌
        response = api_client.post(login_url, user_data)
        refresh_token = response.data['data']['refresh']

        # 使用刷新令牌获取新的访问令牌
        response = api_client.post(refresh_url, {'refresh': refresh_token})
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data['data']

    def test_user_logout(self, api_client, test_user, login_url, logout_url, user_data):
        """测试用户登出"""
        # 先登录
        response = api_client.post(login_url, user_data)
        access_token = response.data['data']['access']
        refresh_token = response.data['data']['refresh']

        # 使用访问令牌登出
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.post(logout_url, {'refresh': refresh_token})
        assert response.status_code == status.HTTP_200_OK

    def test_change_password(self, authenticated_client, change_password_url):
        """测试修改密码"""
        data = {
            'old_password': 'Test123456',
            'new_password': 'NewTestPass456',
            'confirm_password': 'NewTestPass456'
        }
        response = authenticated_client.put(change_password_url, data)
        assert response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_old_password(self, authenticated_client, change_password_url):
        """测试修改密码失败 - 旧密码错误"""
        data = {
            'old_password': 'wrongpass',
            'new_password': 'NewTestPass456',
            'confirm_password': 'NewTestPass456'
        }
        response = authenticated_client.put(change_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST 