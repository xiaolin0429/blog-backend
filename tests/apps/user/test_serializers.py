import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from rest_framework.exceptions import ValidationError
from apps.user.serializers.user import (
    UserRegisterSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer
)

User = get_user_model()

@pytest.mark.django_db
@pytest.mark.unit
class TestUserRegisterSerializer:
    @pytest.fixture
    def valid_data(self):
        return {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Test123456",
            "password2": "Test123456",
            "nickname": "Test User"
        }

    def test_valid_registration(self, valid_data):
        """测试有效的注册数据"""
        serializer = UserRegisterSerializer(data=valid_data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.username == valid_data["username"]
        assert user.email == valid_data["email"]
        assert user.nickname == valid_data["nickname"]
        assert user.check_password(valid_data["password"])

    def test_password_validation(self, valid_data):
        """测试密码验证"""
        # 测试密码不匹配
        data = valid_data.copy()
        data["password2"] = "different"
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password2" in serializer.errors

        # 测试密码过短
        data = valid_data.copy()
        data["password"] = data["password2"] = "short"
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

        # 测试密码缺少数字
        data = valid_data.copy()
        data["password"] = data["password2"] = "TestPassword"
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

        # 测试密码缺少字母
        data = valid_data.copy()
        data["password"] = data["password2"] = "12345678"
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_username_validation(self, valid_data):
        """测试用户名验证"""
        # 测试用户名过短
        data = valid_data.copy()
        data["username"] = "abc"
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "username" in serializer.errors

        # 测试用户名包含特殊字符
        data = valid_data.copy()
        data["username"] = "test@user"
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "username" in serializer.errors

        # 测试用户名重复
        User.objects.create_user(
            username=valid_data["username"],
            email="another@example.com",
            password="testpass123"
        )
        serializer = UserRegisterSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "username" in serializer.errors

    def test_email_validation(self, valid_data):
        """测试邮箱验证"""
        # 测试无效的邮箱格式
        data = valid_data.copy()
        data["email"] = "invalid_email"
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

        # 测试邮箱重复
        User.objects.create_user(
            username="another_user",
            email=valid_data["email"],
            password="testpass123"
        )
        serializer = UserRegisterSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_register_with_invalid_password(self, valid_data):
        """测试密码不符合要求的情况"""
        # 测试纯数字密码
        valid_data["password"] = "12345678"
        serializer = UserRegisterSerializer(data=valid_data)
        assert not serializer.is_valid()
        errors = serializer.errors["password"]
        assert "这个密码太常见了。" in [str(error) for error in errors]
        assert "密码只包含数字。" in [str(error) for error in errors]

        # 测试纯字母密码
        valid_data["password"] = "abcdefgh"
        serializer = UserRegisterSerializer(data=valid_data)
        assert not serializer.is_valid()
        errors = serializer.errors["password"]
        assert "这个密码太常见了。" in [str(error) for error in errors]

@pytest.mark.django_db
@pytest.mark.unit
class TestUserProfileSerializer:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            nickname="Test User",
            bio="Test bio"
        )

    def test_profile_serialization(self, user):
        """测试用户信息序列化"""
        serializer = UserProfileSerializer(user)
        data = serializer.data
        assert data["username"] == user.username
        assert data["email"] == user.email
        assert data["nickname"] == user.nickname
        assert data["bio"] == user.bio
        assert data["avatar"] == settings.DEFAULT_AVATAR_URL

    def test_read_only_fields(self, user):
        """测试只读字段"""
        serializer = UserProfileSerializer(user)
        assert "id" in serializer.data
        assert "date_joined" in serializer.data
        assert "last_login" in serializer.data

@pytest.mark.django_db
@pytest.mark.unit
class TestUserProfileUpdateSerializer:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_update_profile(self, user):
        """测试更新用户信息"""
        data = {
            "nickname": "New Name",
            "bio": "New bio"
        }
        serializer = UserProfileUpdateSerializer(user, data=data, partial=True)
        assert serializer.is_valid()
        updated_user = serializer.save()
        assert updated_user.nickname == data["nickname"]
        assert updated_user.bio == data["bio"]

    def test_update_avatar(self, user):
        """测试更新头像"""
        # 创建一个简单的 1x1 像素的黑色 JPEG 图片
        avatar_content = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff'
            b'\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14'
            b'\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c'
            b' $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c'
            b'\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222'
            b'222222222222\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11'
            b'\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b'
            b'\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00'
            b'\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81'
            b'\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&'
            b"'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89"
            b'\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9'
            b'\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9'
            b'\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8'
            b'\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00'
            b'\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02'
            b'\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04'
            b'\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1'
            b'\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1'
            b'\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstu'
            b'vwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99'
            b'\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9'
            b'\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9'
            b'\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9'
            b'\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xf9\xfe\x8a(\xa0'
            b'\x0f\xff\xd9'
        )
        avatar = SimpleUploadedFile(
            "test_avatar.jpg",
            avatar_content,
            content_type="image/jpeg"
        )
        serializer = UserProfileUpdateSerializer(
            user,
            data={"avatar": avatar},
            partial=True
        )
        assert serializer.is_valid()
        updated_user = serializer.save()
        assert updated_user.avatar is not None

    def test_partial_update(self, user):
        """测试部分更新"""
        data = {"nickname": "New Name"}
        serializer = UserProfileUpdateSerializer(user, data=data, partial=True)
        assert serializer.is_valid()
        updated_user = serializer.save()
        assert updated_user.nickname == data["nickname"]
        assert updated_user.bio == ""  # 保持原值 