from rest_framework import serializers


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
