import pytest
import allure
from django.contrib.auth import get_user_model
from apps.user.serializers import (
    PasswordChangeSerializer,
    LogoutSerializer,
    LoginResponseSerializer
)
from django.utils import timezone
from rest_framework.exceptions import ValidationError

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
            assert not serializer.is_valid()
            assert 'new_password' in serializer.errors

    @allure.story('密码修改')
    @allure.title('测试密码修改序列化器 - 密码格式无效')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.django_db
    def test_password_change_serializer_invalid_password_format(self):
        """测试密码修改序列化器 - 密码格式无效"""
        with allure.step('创建测试用户'):
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='Test123456'
            )
        
        with allure.step('创建请求对象'):
            request = MockRequest(user)
        
        with allure.step('测试纯数字密码'):
            data = {
                'old_password': 'Test123456',
                'new_password': '12345678',
                'confirm_password': '12345678'
            }
            serializer = PasswordChangeSerializer(context={'request': request}, data=data)
            assert not serializer.is_valid()
            assert 'new_password' in serializer.errors
            assert '密码必须包含字母' in str(serializer.errors['new_password'])
        
        with allure.step('测试纯字母密码'):
            data = {
                'old_password': 'Test123456',
                'new_password': 'abcdefgh',
                'confirm_password': 'abcdefgh'
            }
            serializer = PasswordChangeSerializer(context={'request': request}, data=data)
            assert not serializer.is_valid()
            assert 'new_password' in serializer.errors
            assert '密码必须包含数字' in str(serializer.errors['new_password'])

    @allure.story('密码修改')
    @allure.title('测试密码修改序列化器 - 保存密码')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.django_db
    def test_password_change_serializer_save(self):
        """测试密码修改序列化器 - 保存密码"""
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
                'new_password': 'NewTest123456',
                'confirm_password': 'NewTest123456'
            }
        
        with allure.step('验证并保存'):
            serializer = PasswordChangeSerializer(context={'request': request}, data=data)
            assert serializer.is_valid()
            updated_user = serializer.save()
            assert updated_user.check_password('NewTest123456')

    @allure.story('用户登出')
    @allure.title('测试登出序列化器 - 有效数据')
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_serializer_valid(self):
        """测试登出序列化器 - 有效数据"""
        with allure.step('准备测试数据'):
            data = {'refresh': 'valid_refresh_token'}
        
        with allure.step('验证序列化器'):
            serializer = LogoutSerializer(data=data)
            assert serializer.is_valid()
            assert serializer.validated_data['refresh'] == 'valid_refresh_token'

    @allure.story('用户登出')
    @allure.title('测试登出序列化器 - 无效数据')
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_serializer_invalid(self):
        """测试登出序列化器 - 无效数据"""
        with allure.step('测试空数据'):
            serializer = LogoutSerializer(data={})
            assert not serializer.is_valid()
            assert 'refresh' in serializer.errors
        
        with allure.step('测试空令牌'):
            serializer = LogoutSerializer(data={'refresh': ''})
            assert not serializer.is_valid()
            assert 'refresh' in serializer.errors

    @allure.story('登录响应')
    @allure.title('测试登录响应序列化器 - 有效数据')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_response_serializer_valid(self):
        """测试登录响应序列化器 - 有效数据"""
        data = {
            'code': 200,
            'message': 'success',
            'data': {
                'refresh': 'test_refresh_token',
                'access': 'test_access_token',
                'user': {
                    'id': 1,
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'nickname': '测试用户',
                    'avatar': '/media/avatars/default.png',
                    'date_joined': '2024-01-19T21:00:00Z',
                    'last_login': '2024-01-19T21:05:00Z'
                }
            },
            'timestamp': timezone.now(),
            'requestId': 'test_request_id'
        }
        
        serializer = LoginResponseSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.data['code'] == 200
        assert serializer.data['message'] == 'success'
        assert serializer.data['data']['user']['username'] == 'testuser'
        assert serializer.data['requestId'] == 'test_request_id'

    @allure.story('登录响应')
    @allure.title('测试登录响应序列化器 - 缺少必要字段')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_response_serializer_missing_fields(self):
        """测试登录响应序列化器 - 缺少必要字段"""
        # 缺少必要字段
        data = {
            'code': 200,
            'message': 'success'
        }
        
        serializer = LoginResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'data' in serializer.errors
        assert 'timestamp' in serializer.errors
        assert 'requestId' in serializer.errors

    @allure.story('登录响应')
    @allure.title('测试登录响应序列化器 - 无效的数据类型')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_response_serializer_invalid_types(self):
        """测试登录响应序列化器 - 无效的数据类型"""
        data = {
            'code': 'invalid',  # 应该是整数
            'message': 123,  # 应该是字符串
            'data': 'invalid',  # 应该是字典
            'timestamp': 'invalid',  # 应该是日期时间
            'requestId': 123  # 应该是字符串
        }
        
        serializer = LoginResponseSerializer(data=data)
        assert not serializer.is_valid()
        # 验证每个字段的错误信息
        errors = serializer.errors
        assert '请填写合法的整数值' in str(errors.get('code', []))
        assert '期望是包含类目的字典' in str(errors.get('data', []))
        assert '日期时间格式错误' in str(errors.get('timestamp', []))

    @allure.story('登录响应')
    @allure.title('测试登录响应序列化器 - 空数据')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_response_serializer_empty_data(self):
        """测试登录响应序列化器 - 空数据"""
        serializer = LoginResponseSerializer(data={})
        assert not serializer.is_valid()
        assert 'code' in serializer.errors
        assert 'message' in serializer.errors
        assert 'data' in serializer.errors
        assert 'timestamp' in serializer.errors
        assert 'requestId' in serializer.errors 