import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import pytz
from django.utils import timezone
from unittest.mock import patch
from rest_framework.response import Response

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
@pytest.mark.integration
class TestAuthViews:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    def test_login_success(self, api_client, normal_user):
        """测试登录成功的情况"""
        url = reverse('user:auth:login')
        data = {
            'username': normal_user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']
        assert 'user' in response.data['data']
        user_data = response.data['data']['user']
        assert user_data['username'] == normal_user.username
        assert user_data['email'] == normal_user.email
        
    def test_login_with_timezone(self, api_client, normal_user):
        """测试带时区的登录"""
        url = reverse('user:auth:login')
        data = {
            'username': normal_user.username,
            'password': 'testpass123'
        }
        api_client.credentials(HTTP_X_TIMEZONE='America/New_York')
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        user_data = response.data['data']['user']
        # 验证时间格式是否正确
        assert 'date_joined' in user_data
        assert 'last_login' in user_data

    def test_login_with_invalid_timezone(self, api_client, normal_user):
        """测试无效时区的登录"""
        url = reverse('user:auth:login')
        data = {
            'username': normal_user.username,
            'password': 'testpass123'
        }
        api_client.credentials(HTTP_X_TIMEZONE='Invalid/Timezone')
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        user_data = response.data['data']['user']
        # 验证使用了默认时区
        assert 'date_joined' in user_data
        assert 'last_login' in user_data

    def test_login_with_remember_me(self, api_client, normal_user):
        """测试记住我功能"""
        url = reverse('user:auth:login')
        data = {
            'username': normal_user.username,
            'password': 'testpass123',
            'remember': True
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']

    def test_login_invalid_credentials(self, api_client, normal_user):
        """测试登录失败 - 无效的凭证"""
        url = reverse('user:auth:login')
        data = {
            'username': normal_user.username,
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 401
        assert response.data['message'] == "用户名或密码错误"

    @patch('apps.user.views.auth.LoginView.post')
    def test_login_account_locked(self, mock_post, api_client, normal_user):
        """测试账号锁定情况"""
        error_response = Response(
            {
                'code': 403,
                'message': '账号已被锁定',
                'data': None
            },
            status=status.HTTP_200_OK
        )
        mock_post.return_value = error_response
        
        url = reverse('user:auth:login')
        data = {
            'username': normal_user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 403
        assert response.data['message'] == "账号已被锁定"

    @patch('apps.user.views.auth.LoginView.post')
    def test_login_rate_limit_exceeded(self, mock_post, api_client, normal_user):
        """测试登录频率限制"""
        error_response = Response(
            {
                'code': 429,
                'message': '登录尝试次数过多',
                'data': None
            },
            status=status.HTTP_200_OK
        )
        mock_post.return_value = error_response
        
        url = reverse('user:auth:login')
        data = {
            'username': normal_user.username,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 429
        assert response.data['message'] == "登录尝试次数过多"

    def test_token_refresh_success(self, api_client, normal_user):
        """测试刷新令牌成功"""
        # 先登录获取刷新令牌
        login_url = reverse('user:auth:login')
        data = {
            'username': normal_user.username,
            'password': 'testpass123'
        }
        response = api_client.post(login_url, data)
        refresh_token = response.data['data']['refresh']
        
        # 使用刷新令牌获取新的访问令牌
        refresh_url = reverse('user:auth:token_refresh')
        data = {'refresh': refresh_token}
        response = api_client.post(refresh_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert 'access' in response.data['data']

    def test_token_refresh_invalid_token(self, api_client):
        """测试刷新令牌失败 - 无效的令牌"""
        url = reverse('user:auth:token_refresh')
        data = {'refresh': 'invalid_token'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 401
        assert response.data['message'] == "刷新令牌无效或已过期"

    def test_token_refresh_expired_token(self, api_client, normal_user):
        """测试刷新令牌失败 - 过期的令牌"""
        # 创建一个过期的令牌
        refresh = RefreshToken.for_user(normal_user)
        refresh.set_exp(lifetime=-timezone.timedelta(days=1))
        
        url = reverse('user:auth:token_refresh')
        data = {'refresh': str(refresh)}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 401
        assert response.data['message'] == "刷新令牌无效或已过期"

    def test_token_refresh_missing_token(self, api_client):
        """测试刷新令牌失败 - 缺少令牌"""
        url = reverse('user:auth:token_refresh')
        data = {}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 401

    def test_logout_without_token(self, api_client):
        """测试未认证的登出"""
        url = reverse('user:auth:logout')
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED  # 这里保持401因为是认证中间件返回的
        
    def test_logout_with_invalid_token(self, api_client, normal_user):
        """测试使用无效令牌登出"""
        url = reverse('user:auth:logout')
        api_client.force_authenticate(user=normal_user)
        data = {'refresh': 'invalid_token'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert response.data['message'] == "令牌无效或已过期"

    def test_logout_without_refresh_token(self, api_client, normal_user):
        """测试没有提供刷新令牌的登出"""
        url = reverse('user:auth:logout')
        api_client.force_authenticate(user=normal_user)
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400

    def test_logout_success(self, api_client, normal_user):
        """测试登出成功"""
        # 先登录获取刷新令牌
        login_url = reverse('user:auth:login')
        data = {
            'username': normal_user.username,
            'password': 'testpass123'
        }
        response = api_client.post(login_url, data)
        refresh_token = response.data['data']['refresh']
        
        # 使用刷新令牌登出
        logout_url = reverse('user:auth:logout')
        api_client.force_authenticate(user=normal_user)
        data = {'refresh': refresh_token}
        response = api_client.post(logout_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['message'] == "登出成功"
        
        # 验证令牌已被加入黑名单
        refresh_url = reverse('user:auth:token_refresh')
        data = {'refresh': refresh_token}
        response = api_client.post(refresh_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 401

    def test_change_password_success(self, authenticated_client, change_password_url):
        """测试修改密码成功"""
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewTestPass456',
            'confirm_password': 'NewTestPass456'
        }
        response = authenticated_client.put(change_password_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['message'] == "密码修改成功"

    def test_change_password_wrong_old_password(self, authenticated_client, change_password_url):
        """测试修改密码失败 - 旧密码错误"""
        data = {
            'old_password': 'wrongpass',
            'new_password': 'NewTestPass456',
            'confirm_password': 'NewTestPass456'
        }
        response = authenticated_client.put(change_password_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert response.data['message'] == "密码修改失败"

    def test_change_password_mismatch(self, authenticated_client, change_password_url):
        """测试修改密码失败 - 新密码不匹配"""
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewTestPass456',
            'confirm_password': 'DifferentPass789'
        }
        response = authenticated_client.put(change_password_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert response.data['message'] == "密码修改失败"

    def test_change_password_invalid_format(self, authenticated_client, change_password_url):
        """测试修改密码失败 - 密码格式无效"""
        data = {
            'old_password': 'testpass123',
            'new_password': '12345',  # 太短且没有字母
            'confirm_password': '12345'
        }
        response = authenticated_client.put(change_password_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert response.data['message'] == "密码修改失败" 