from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

import pytest

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """用户模型测试"""

    def test_create_user(self, user_data):
        """测试创建用户"""
        user = User.objects.create_user(**user_data)
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.nickname == user_data["nickname"]
        assert user.bio == user_data["bio"]
        assert user.check_password(user_data["password"])
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_superuser(self):
        """测试创建超级用户"""
        admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="Admin123456"
        )
        assert admin_user.is_staff
        assert admin_user.is_superuser

    def test_user_str(self, test_user, user_data):
        """测试用户字符串表示"""
        assert str(test_user) == user_data["username"]

    def test_user_email_unique(self, test_user, user_data):
        """测试用户邮箱唯一性"""
        duplicate_user = User(
            username="another", email=user_data["email"], password="Test123456"
        )
        with pytest.raises(ValidationError):
            duplicate_user.full_clean()

    def test_user_username_unique(self, test_user, user_data):
        """测试用户名唯一性"""
        duplicate_user = User(
            username=user_data["username"],
            email="another@example.com",
            password="Test123456",
        )
        with pytest.raises(ValidationError):
            duplicate_user.full_clean()

    def test_user_optional_fields(self):
        """测试用户可选字段"""
        user = User.objects.create_user(
            username="minimal", email="minimal@example.com", password="Test123456"
        )
        assert user.nickname == ""  # 默认为空字符串
        assert user.bio == ""  # 默认为空字符串
        assert not user.avatar  # 头像为空

    def test_user_avatar_upload(self, test_user):
        """测试用户头像上传路径"""
        assert test_user.avatar.field.upload_to == "avatars/"
