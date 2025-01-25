from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from apps.core.serializers import TimezoneSerializerMixin

User = get_user_model()


class LoginResponseSerializer(serializers.Serializer):
    """登录响应序列化器"""

    code = serializers.IntegerField(help_text="状态码")
    message = serializers.CharField(help_text="状态信息")
    data = serializers.DictField(help_text="响应数据")
    timestamp = serializers.DateTimeField(help_text="时间戳")
    requestId = serializers.CharField(help_text="请求ID")

    class Meta:
        swagger_schema_fields = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
                    "user": {
                        "id": 1,
                        "username": "admin",
                        "email": "admin@example.com",
                        "nickname": "管理员",
                        "avatar": "/media/avatars/default.png",
                        "date_joined": "2024-01-19 21:00:00",
                        "last_login": "2024-01-19 21:05:00",
                    },
                },
                "timestamp": "2024-01-19T21:05:00Z",
                "requestId": "req_123456789",
            }
        }


class LogoutSerializer(serializers.Serializer):
    """登出请求序列化器"""

    refresh = serializers.CharField(help_text="刷新令牌")


class PasswordChangeSerializer(serializers.Serializer):
    """密码修改序列化器"""

    old_password = serializers.CharField(help_text="旧密码")
    new_password = serializers.CharField(help_text="新密码")
    confirm_password = serializers.CharField(help_text="确认密码")

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"new_password": "两次密码不一致"})

        # 验证密码复杂度
        password = attrs["new_password"]
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError({"new_password": "密码必须包含数字"})
        if not any(char.isalpha() for char in password):
            raise serializers.ValidationError({"new_password": "密码必须包含字母"})

        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value

    def save(self, **kwargs):
        password = self.validated_data["new_password"]
        user = self.context["request"].user
        user.set_password(password)
        user.save()
        return user
