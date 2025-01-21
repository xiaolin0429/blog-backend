import pytest
from django.contrib.auth import get_user_model
from apps.user.serializers import (
    PasswordChangeSerializer,
    LogoutSerializer
)

User = get_user_model()

@pytest.fixture
def password_change_data():
    """返回密码修改数据"""
    return {
        'old_password': 'Test123456',
        'new_password': 'NewTest123456',
        'confirm_password': 'NewTest123456'
    }

@pytest.fixture
def mock_request(test_user):
    """模拟请求对象"""
    class MockRequest:
        def __init__(self, user):
            self.user = user
    return MockRequest(test_user)

@pytest.mark.django_db
class TestAuthSerializer:
    """认证序列化器测试"""

    def test_password_change_serializer_valid(self, test_user, password_change_data, mock_request):
        """测试密码修改序列化器-有效数据"""
        serializer = PasswordChangeSerializer(
            data=password_change_data,
            context={'request': mock_request}
        )
        assert serializer.is_valid()

    def test_password_change_serializer_wrong_old_password(self, test_user, password_change_data, mock_request):
        """测试密码修改序列化器-旧密码错误"""
        data = password_change_data.copy()
        data['old_password'] = 'WrongPassword'
        serializer = PasswordChangeSerializer(
            data=data,
            context={'request': mock_request}
        )
        assert not serializer.is_valid()
        assert 'old_password' in serializer.errors

    def test_password_change_serializer_password_mismatch(self, test_user, password_change_data, mock_request):
        """测试密码修改序列化器-新密码不匹配"""
        data = password_change_data.copy()
        data['confirm_password'] = 'Different123456'
        serializer = PasswordChangeSerializer(
            data=data,
            context={'request': mock_request}
        )
        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors or 'confirm_password' in serializer.errors

    def test_logout_serializer(self):
        """测试登出序列化器"""
        data = {'refresh': 'dummy-refresh-token'}
        serializer = LogoutSerializer(data=data)
        assert serializer.is_valid() 