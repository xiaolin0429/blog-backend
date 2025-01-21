import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

@pytest.fixture
def login_url():
    """返回登录URL"""
    return reverse('auth:login')

@pytest.fixture
def refresh_url():
    """返回刷新令牌URL"""
    return reverse('auth:token_refresh')

@pytest.fixture
def logout_url():
    """返回登出URL"""
    return reverse('auth:logout')

@pytest.fixture
def change_password_url():
    """返回修改密码URL"""
    return reverse('auth:password_change')

@pytest.mark.django_db
class TestAuthView:
    """认证视图测试"""

    def test_user_login(self, api_client, test_user, login_url, user_data):
        """测试用户登录"""
        data = {
            'username': user_data['username'],
            'password': user_data['password']
        }
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert 'data' in response.data
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']
        assert 'user' in response.data['data']

    def test_user_login_invalid_credentials(self, api_client, login_url):
        """测试用户登录-无效凭证"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['code'] == 401
        assert response.data['message'] == "用户名或密码错误"

    def test_token_refresh(self, api_client, test_user, login_url, refresh_url, user_data):
        """测试令牌刷新"""
        # 先登录获取refresh token
        login_data = {
            'username': user_data['username'],
            'password': user_data['password']
        }
        login_response = api_client.post(login_url, login_data)
        assert login_response.status_code == status.HTTP_200_OK
        refresh_token = login_response.data['data']['refresh']

        # 使用refresh token获取新的access token
        refresh_data = {'refresh': refresh_token}
        response = api_client.post(refresh_url, refresh_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert 'access' in response.data['data']

    def test_user_logout(self, api_client, test_user, login_url, logout_url, user_data):
        """测试用户登出"""
        # 先登录获取token
        login_data = {
            'username': user_data['username'],
            'password': user_data['password']
        }
        login_response = api_client.post(login_url, login_data)
        assert login_response.status_code == status.HTTP_200_OK
        refresh_token = login_response.data['data']['refresh']
        access_token = login_response.data['data']['access']

        # 设置认证头
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # 登出
        logout_data = {'refresh': refresh_token}
        response = api_client.post(logout_url, logout_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['message'] == "登出成功"

    def test_change_password(self, authenticated_client, change_password_url):
        """测试修改密码"""
        data = {
            'old_password': 'Test123456',
            'new_password': 'NewTest123456',
            'new_password2': 'NewTest123456'
        }
        response = authenticated_client.post(change_password_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200

        # 验证新密码是否生效
        authenticated_client.logout()
        login_data = {
            'username': 'testuser',
            'password': 'NewTest123456'
        }
        response = authenticated_client.post(reverse('user:login'), login_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200

    def test_change_password_wrong_old_password(self, authenticated_client, change_password_url):
        """测试修改密码-旧密码错误"""
        data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewTest123456',
            'new_password2': 'NewTest123456'
        }
        response = authenticated_client.post(change_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST 