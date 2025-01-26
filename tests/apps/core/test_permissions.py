from django.contrib.auth import get_user_model

import allure
import pytest
from rest_framework.test import APIRequestFactory

from apps.core.permissions import IsAdminUserOrReadOnly

User = get_user_model()


@allure.epic("核心功能")
@allure.feature("权限管理")
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

    @allure.story("安全方法访问")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试匿名用户可以访问安全方法(GET、HEAD、OPTIONS)")
    @pytest.mark.security
    def test_safe_methods_allowed_for_anonymous(self, permission, rf):
        """测试匿名用户可以访问安全方法"""
        with allure.step("测试每个安全方法"):
            for method in ["get", "head", "options"]:
                with allure.step(f"测试 {method.upper()} 方法"):
                    request = getattr(rf, method)("/")
                    request.user = None
                    assert permission.has_permission(request, None)

    @allure.story("安全方法访问")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试普通用户可以访问安全方法(GET、HEAD、OPTIONS)")
    @pytest.mark.security
    def test_safe_methods_allowed_for_normal_user(self, permission, rf, normal_user):
        """测试普通用户可以访问安全方法"""
        with allure.step("测试每个安全方法"):
            for method in ["get", "head", "options"]:
                with allure.step(f"测试 {method.upper()} 方法"):
                    request = getattr(rf, method)("/")
                    request.user = normal_user
                    assert permission.has_permission(request, None)

    @allure.story("不安全方法访问")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("测试匿名用户不能访问不安全方法(POST、PUT、PATCH、DELETE)")
    @pytest.mark.security
    def test_unsafe_methods_denied_for_anonymous(self, permission, rf):
        """测试匿名用户不能访问不安全方法"""
        with allure.step("测试每个不安全方法"):
            for method in ["post", "put", "patch", "delete"]:
                with allure.step(f"测试 {method.upper()} 方法"):
                    request = getattr(rf, method)("/")
                    request.user = None
                    assert not permission.has_permission(request, None)

    @allure.story("不安全方法访问")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("测试普通用户不能访问不安全方法(POST、PUT、PATCH、DELETE)")
    @pytest.mark.security
    def test_unsafe_methods_denied_for_normal_user(self, permission, rf, normal_user):
        """测试普通用户不能访问不安全方法"""
        with allure.step("测试每个不安全方法"):
            for method in ["post", "put", "patch", "delete"]:
                with allure.step(f"测试 {method.upper()} 方法"):
                    request = getattr(rf, method)("/")
                    request.user = normal_user
                    assert not permission.has_permission(request, None)

    @allure.story("管理员权限")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试管理员可以访问所有方法，包括不安全方法")
    @pytest.mark.security
    def test_unsafe_methods_allowed_for_staff(self, permission, rf, staff_user):
        """测试管理员可以访问不安全方法"""
        with allure.step("测试每个不安全方法"):
            for method in ["post", "put", "patch", "delete"]:
                with allure.step(f"测试 {method.upper()} 方法"):
                    request = getattr(rf, method)("/")
                    request.user = staff_user
                    assert permission.has_permission(request, None)

    @allure.story("超级用户权限")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试超级用户可以访问所有方法，包括不安全方法")
    @pytest.mark.security
    def test_unsafe_methods_allowed_for_superuser(self, permission, rf, admin_user):
        """测试超级用户可以访问不安全方法"""
        with allure.step("测试每个不安全方法"):
            for method in ["post", "put", "patch", "delete"]:
                with allure.step(f"测试 {method.upper()} 方法"):
                    request = getattr(rf, method)("/")
                    request.user = admin_user
                    assert permission.has_permission(request, None)
