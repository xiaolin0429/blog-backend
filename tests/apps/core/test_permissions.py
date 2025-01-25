from django.contrib.auth import get_user_model

import pytest
from rest_framework.test import APIRequestFactory

from apps.core.permissions import IsAdminUserOrReadOnly

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestIsAdminUserOrReadOnly:
    @pytest.fixture
    def permission(self):
        return IsAdminUserOrReadOnly()

    @pytest.fixture
    def rf(self):
        return APIRequestFactory()

    @pytest.fixture
    def normal_user(self):
        return User.objects.create_user(
            username="normal_user", email="normal@example.com", password="testpass123"
        )

    @pytest.fixture
    def admin_user(self):
        return User.objects.create_superuser(
            username="admin_user", email="admin@example.com", password="testpass123"
        )

    @pytest.fixture
    def staff_user(self):
        return User.objects.create_user(
            username="staff_user",
            email="staff@example.com",
            password="testpass123",
            is_staff=True,
        )

    def test_safe_methods_allowed_for_anonymous(self, permission, rf):
        """测试匿名用户可以访问安全方法"""
        for method in ["get", "head", "options"]:
            request = getattr(rf, method)("/")
            request.user = None
            assert permission.has_permission(request, None)

    def test_safe_methods_allowed_for_normal_user(self, permission, rf, normal_user):
        """测试普通用户可以访问安全方法"""
        for method in ["get", "head", "options"]:
            request = getattr(rf, method)("/")
            request.user = normal_user
            assert permission.has_permission(request, None)

    def test_unsafe_methods_denied_for_anonymous(self, permission, rf):
        """测试匿名用户不能访问不安全方法"""
        for method in ["post", "put", "patch", "delete"]:
            request = getattr(rf, method)("/")
            request.user = None
            assert not permission.has_permission(request, None)

    def test_unsafe_methods_denied_for_normal_user(self, permission, rf, normal_user):
        """测试普通用户不能访问不安全方法"""
        for method in ["post", "put", "patch", "delete"]:
            request = getattr(rf, method)("/")
            request.user = normal_user
            assert not permission.has_permission(request, None)

    def test_unsafe_methods_allowed_for_staff(self, permission, rf, staff_user):
        """测试管理员可以访问不安全方法"""
        for method in ["post", "put", "patch", "delete"]:
            request = getattr(rf, method)("/")
            request.user = staff_user
            assert permission.has_permission(request, None)

    def test_unsafe_methods_allowed_for_superuser(self, permission, rf, admin_user):
        """测试超级用户可以访问不安全方法"""
        for method in ["post", "put", "patch", "delete"]:
            request = getattr(rf, method)("/")
            request.user = admin_user
            assert permission.has_permission(request, None)
