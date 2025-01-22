import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user_data():
    """返回用于创建用户的基本数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "nickname": "Test User",
        "bio": "This is a test user"
    }

@pytest.fixture
def normal_user(user_data):
    """创建并返回一个普通用户"""
    return User.objects.create_user(**user_data)

@pytest.fixture
def admin_user(user_data):
    """创建并返回一个管理员用户"""
    return User.objects.create_superuser(**user_data)

@pytest.fixture
def staff_user(user_data):
    """创建并返回一个职员用户"""
    user_data["username"] = "staffuser"
    user_data["email"] = "staff@example.com"
    user = User.objects.create_user(**user_data)
    user.is_staff = True
    user.save()
    return user 