import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestUserModel:
    @pytest.fixture
    def user_data(self):
        return {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "nickname": "Test User",
            "bio": "This is a test user",
        }

    def test_create_user(self, user_data):
        """测试创建普通用户"""
        user = User.objects.create_user(**user_data)
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.nickname == user_data["nickname"]
        assert user.bio == user_data["bio"]
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active
        assert user.check_password(user_data["password"])

    def test_create_superuser(self, user_data):
        """测试创建超级用户"""
        user = User.objects.create_superuser(**user_data)
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.is_staff
        assert user.is_superuser
        assert user.is_active

    def test_user_str_method(self, user_data):
        """测试用户模型的字符串表示"""
        user = User.objects.create_user(**user_data)
        assert str(user) == user_data["username"]

    def test_email_unique(self, user_data):
        """测试邮箱唯一性约束"""
        User.objects.create_user(**user_data)
        duplicate_user = user_data.copy()
        duplicate_user["username"] = "another_user"
        with pytest.raises(IntegrityError):
            User.objects.create_user(**duplicate_user)

    def test_username_unique(self, user_data):
        """测试用户名唯一性约束"""
        User.objects.create_user(**user_data)
        duplicate_user = user_data.copy()
        duplicate_user["email"] = "another@example.com"
        with pytest.raises(IntegrityError):
            User.objects.create_user(**duplicate_user)

    def test_optional_fields(self):
        """测试可选字段"""
        user = User.objects.create_user(
            username="minimaluser", email="minimal@example.com", password="testpass123"
        )
        assert user.nickname == ""  # 默认值
        assert user.bio == ""  # 默认值
        assert not bool(user.avatar)  # 检查 avatar 是否为空

    def test_ordering(self, user_data):
        """测试用户排序"""
        # 创建第一个用户
        user1 = User.objects.create_user(**user_data)
        user1.date_joined = timezone.now() - datetime.timedelta(hours=1)
        user1.save()

        # 创建第二个用户
        user2_data = user_data.copy()
        user2_data.update({"username": "testuser2", "email": "test2@example.com"})
        user2 = User.objects.create_user(**user2_data)
        user2.date_joined = timezone.now()
        user2.save()

        users = User.objects.all()
        assert users[0] == user2  # 后创建的用户应该在前面
        assert users[1] == user1
