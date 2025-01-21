import pytest
import allure
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
        'new_password2': 'NewTest123456'
    }

class MockRequest:
    def __init__(self, user):
        self.user = user

@allure.epic('用户认证')
@allure.feature('认证序列化器')
class TestAuthSerializer:
    """认证序列化器测试"""

    @allure.story('密码修改')
    @allure.title('测试密码修改序列化器 - 有效数据')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.django_db
    def test_password_change_serializer_valid(self):
        """测试密码修改序列化器 - 有效数据"""
        with allure.step('创建测试用户'):
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='Test123456'
            )
        
        with allure.step('创建请求对象'):
            request = MockRequest(user)
        
        with allure.step('准备测试数据'):
            data = {
                'old_password': 'Test123456',
                'new_password': 'NewTestPass456',
                'confirm_password': 'NewTestPass456'
            }
        
        with allure.step('验证序列化器'):
            serializer = PasswordChangeSerializer(context={'request': request}, data=data)
            assert serializer.is_valid()

    @allure.story('密码修改')
    @allure.title('测试密码修改序列化器 - 旧密码错误')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.django_db
    def test_password_change_serializer_wrong_old_password(self):
        """测试密码修改序列化器 - 旧密码错误"""
        with allure.step('创建测试用户'):
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='Test123456'
            )
        
        with allure.step('创建请求对象'):
            request = MockRequest(user)
        
        with allure.step('准备测试数据'):
            data = {
                'old_password': 'WrongPass123',
                'new_password': 'NewTestPass456',
                'confirm_password': 'NewTestPass456'
            }
        
        with allure.step('验证序列化器'):
            serializer = PasswordChangeSerializer(context={'request': request}, data=data)
            assert not serializer.is_valid()
            assert 'old_password' in serializer.errors

    @allure.story('密码修改')
    @allure.title('测试密码修改序列化器 - 密码不匹配')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.django_db
    def test_password_change_serializer_password_mismatch(self):
        """测试密码修改序列化器 - 密码不匹配"""
        with allure.step('创建测试用户'):
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='Test123456'
            )
        
        with allure.step('创建请求对象'):
            request = MockRequest(user)
        
        with allure.step('准备测试数据'):
            data = {
                'old_password': 'Test123456',
                'new_password': 'NewTestPass456',
                'confirm_password': 'DifferentPass789'
            }
        
        with allure.step('验证序列化器'):
            serializer = PasswordChangeSerializer(context={'request': request}, data=data)
            serializer.is_valid()
            assert 'new_password' in serializer.errors

    @allure.story('用户登出')
    @allure.title('测试登出序列化器')
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_serializer(self):
        """测试登出序列化器"""
        with allure.step('准备测试数据'):
            data = {'refresh': 'dummy-refresh-token'}
        
        with allure.step('验证序列化器'):
            serializer = LogoutSerializer(data=data)
            assert serializer.is_valid() 