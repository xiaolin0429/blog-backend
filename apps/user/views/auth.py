import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from apps.core.response import error_response, success_response

from ..serializers import LoginResponseSerializer, LogoutSerializer

User = get_user_model()


class LoginView(TokenObtainPairView):
    """用户登录视图"""

    @swagger_auto_schema(
        operation_summary="用户登录",
        operation_description="用户登录接口，成功后返回访问令牌和刷新令牌",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="用户名"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="密码"),
                "remember": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, description="记住我"
                ),
            },
        ),
        responses={
            200: LoginResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            tokens = serializer.validated_data

            # 更新最后登录时间
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            # 获取用户时区
            user_timezone = request.headers.get("X-Timezone", "Asia/Shanghai")
            try:
                user_tz = pytz.timezone(user_timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                user_tz = pytz.timezone("Asia/Shanghai")

            # 转换时间到用户时区
            date_joined = user.date_joined.astimezone(user_tz)
            last_login = user.last_login.astimezone(user_tz)

            data = {
                "refresh": tokens["refresh"],
                "access": tokens["access"],
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "nickname": getattr(user, "nickname", ""),
                    "avatar": user.avatar.url
                    if user.avatar and hasattr(user.avatar, "url")
                    else settings.DEFAULT_AVATAR_URL,
                    "date_joined": date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                    "last_login": last_login.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
            return success_response(data=data)
        except Exception as e:
            error_code = 401
            error_msg = "用户名或密码错误"
            if hasattr(e, "detail"):
                if "locked" in str(e.detail).lower():
                    error_code = 403
                    error_msg = "账号已被锁定"
                elif "many" in str(e.detail).lower():
                    error_code = 429
                    error_msg = "登录尝试次数过多"
            return error_response(code=error_code, message=error_msg)


class TokenRefreshView(BaseTokenRefreshView):
    """刷新令牌视图"""

    @swagger_auto_schema(
        operation_summary="刷新访问令牌",
        operation_description="使用刷新令牌获取新的访问令牌",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="刷新令牌"),
            },
        ),
        responses={
            200: openapi.Response(
                description="成功",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(
                            type=openapi.TYPE_STRING, description="新的访问令牌"
                        ),
                    },
                ),
            )
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = {"access": serializer.validated_data["access"]}
            return success_response(data=data)
        except Exception as e:
            return error_response(code=401, message="刷新令牌无效或已过期")


class LogoutView(generics.GenericAPIView):
    """用户登出视图"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        operation_summary="用户登出",
        operation_description="用户登出，使当前token失效",
        responses={
            200: openapi.Response(
                description="登出成功",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="状态码"
                        ),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, description="状态信息"
                        ),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT, description="响应数据"
                        ),
                    },
                ),
            )
        },
        security=[{"Bearer": []}],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            refresh_token = serializer.validated_data["refresh"]
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return success_response(message="登出成功", data=None)
            except TokenError:
                return error_response(code=400, message="令牌无效或已过期")
        except Exception as e:
            error_msg = "登出失败"
            if hasattr(e, "detail"):
                error_msg = str(e.detail)
            return error_response(code=400, message=error_msg)
