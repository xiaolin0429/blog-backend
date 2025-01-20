import pytest
from django.contrib.auth import get_user_model
from apps.user.serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer
)

User = get_user_model()

@pytest.fixture
def valid_register_data():
    """返回有效的注册数据"""
    return {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'NewTest123456',
        'password2': 'NewTest123456'
    }

@pytest.mark.django_db
class TestUserSerializer:
    """用户序列化器测试"""

    def test_user_register_serializer_valid(self, valid_register_data):
        """测试用户注册序列化器-有效数据"""
        serializer = UserRegisterSerializer(data=valid_register_data)
        assert serializer.is_valid()

    def test_user_register_serializer_password_mismatch(self, valid_register_data):
        """测试用户注册序列化器-密码不匹配"""
        data = valid_register_data.copy()
        data['password2'] = 'Different123456'
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password2' in serializer.errors

    def test_user_register_serializer_duplicate_username(self, test_user, valid_register_data):
        """测试用户注册序列化器-用户名重复"""
        data = valid_register_data.copy()
        data['username'] = test_user.username
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'username' in serializer.errors

    def test_user_profile_serializer(self, test_user):
        """测试用户资料序列化器"""
        serializer = UserProfileSerializer(test_user)
        data = serializer.data
        assert data['username'] == test_user.username
        assert data['email'] == test_user.email
        assert data['nickname'] == test_user.nickname
        assert data['bio'] == test_user.bio

    def test_user_profile_update_serializer_valid(self, test_user):
        """测试用户资料更新序列化器-有效数据"""
        update_data = {
            'nickname': 'Updated User',
            'bio': 'Updated bio'
        }
        serializer = UserProfileUpdateSerializer(
            test_user,
            data=update_data,
            partial=True
        )
        assert serializer.is_valid()
        updated_user = serializer.save()
        assert updated_user.nickname == 'Updated User'
        assert updated_user.bio == 'Updated bio' 