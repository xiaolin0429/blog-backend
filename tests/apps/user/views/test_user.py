import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

import pytest
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture(autouse=True)
def setup_test_media():
    """设置测试媒体目录"""
    media_root = settings.MEDIA_ROOT
    avatars_dir = os.path.join(media_root, "avatars")
    os.makedirs(avatars_dir, exist_ok=True)
    yield
    # 清理测试文件
    for root, dirs, files in os.walk(media_root):
        for file in files:
            os.remove(os.path.join(root, file))


@pytest.fixture
def register_url():
    """返回注册URL"""
    return "/api/v1/user/register/"


@pytest.fixture
def profile_url():
    """返回用户资料URL"""
    return "/api/v1/user/me/"


@pytest.fixture
def test_image_path():
    """返回测试图片的路径"""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "resources",
        "test_avatar.png",
    )


@pytest.mark.django_db
@pytest.mark.integration
class TestUserViews:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def valid_user_data(self):
        return {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Test123456",
            "password2": "Test123456",
            "nickname": "New User",
        }

    def test_register_success(self, api_client):
        """测试成功注册"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "password2": "testpass123",
            "nickname": "Test User",
        }
        response = api_client.post(reverse("user:register"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert "id" in response.data["data"]
        assert response.data["data"]["username"] == "testuser"
        assert response.data["data"]["email"] == "test@example.com"
        assert response.data["data"]["nickname"] == "Test User"

    def test_register_duplicate_username(self, api_client, normal_user):
        """测试注册重复用户名"""
        url = reverse("user:register")
        data = {
            "username": normal_user.username,
            "email": "another@example.com",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "nickname": "Another User",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert "username" in response.data["data"]["errors"]

    def test_register_invalid_data(self, api_client):
        """测试注册数据无效"""
        url = reverse("user:register")
        data = {
            "username": "test",  # 用户名太短
            "email": "invalid-email",  # 无效的邮箱
            "password": "123",  # 密码太短
            "confirm_password": "123",
            "nickname": "",  # 昵称为空
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert "errors" in response.data["data"]

    def test_get_profile_unauthorized(self, api_client):
        """测试未登录获取个人信息"""
        url = reverse("user:profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_profile_success(self, api_client, normal_user):
        """测试获取个人信息成功"""
        url = reverse("user:profile")
        api_client.force_authenticate(user=normal_user)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["username"] == normal_user.username
        assert response.data["data"]["email"] == normal_user.email

    def test_update_profile_success(self, api_client, normal_user):
        """测试更新个人信息成功"""
        url = reverse("user:profile")
        api_client.force_authenticate(user=normal_user)
        data = {"nickname": "Updated Name", "bio": "Updated bio"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["nickname"] == "Updated Name"
        assert response.data["data"]["bio"] == "Updated bio"

    def test_update_profile_invalid_data(self, api_client, normal_user):
        """测试更新个人信息失败 - 无效数据"""
        url = reverse("user:profile")
        api_client.force_authenticate(user=normal_user)
        data = {"nickname": "", "bio": "x" * 1000}  # 昵称不能为空  # 个人简介太长
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert "errors" in response.data["data"]

    def test_change_password_success(self, normal_user, api_client):
        """测试成功修改密码"""
        api_client.force_authenticate(user=normal_user)
        data = {
            "old_password": "testpass123",
            "new_password": "newtestpass123",
            "confirm_password": "newtestpass123",
        }
        response = api_client.put(reverse("user:password_change"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["message"] == "密码修改成功"

    def test_change_password_wrong_old_password(self, normal_user, api_client):
        """测试使用错误的旧密码修改密码"""
        api_client.force_authenticate(user=normal_user)
        data = {
            "old_password": "wrong_password",
            "new_password": "new_password123",
            "confirm_password": "new_password123",
        }
        response = api_client.put(reverse("user:password_change"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert response.data["data"]["old_password"][0] == "旧密码不正确"

    def test_user_register(self, api_client, register_url):
        """测试用户注册"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "NewTest123456",
            "password2": "NewTest123456",
        }
        response = api_client.post(register_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert "id" in response.data["data"]
        assert response.data["data"]["username"] == "newuser"
        assert User.objects.filter(username="newuser").exists()

    def test_user_register_duplicate_username(
        self, api_client, test_user, register_url
    ):
        """测试用户注册-用户名重复"""
        data = {
            "username": test_user.username,
            "email": "another@example.com",
            "password": "Test123456",
            "password2": "Test123456",
        }
        response = api_client.post(register_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert "username" in response.data["data"]["errors"]

    def test_user_register_duplicate_email(self, api_client, test_user, register_url):
        """测试用户注册-邮箱重复"""
        data = {
            "username": "anotheruser",
            "email": test_user.email,
            "password": "Test123456",
            "password2": "Test123456",
        }
        response = api_client.post(register_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert "email" in response.data["data"]["errors"]

    def test_get_user_profile_unauthenticated(self, api_client, profile_url):
        """测试未认证用户获取用户资料"""
        response = api_client.get(profile_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_profile(self, authenticated_client, profile_url):
        """测试更新用户资料"""
        data = {"nickname": "Updated User", "bio": "Updated bio"}
        response = authenticated_client.patch(profile_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["nickname"] == "Updated User"
        assert response.data["data"]["bio"] == "Updated bio"

    def test_update_user_profile_unauthenticated(self, api_client, profile_url):
        """测试未认证用户更新用户资料"""
        data = {"nickname": "Updated User", "bio": "Updated bio"}
        response = api_client.patch(profile_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
