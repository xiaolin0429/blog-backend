# Standard Library
import logging

# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# Third Party
from rest_framework import generics, permissions, serializers

# Local
from apps.core.response import error_response, success_response

from ..serializers.auth import PasswordChangeSerializer
from ..serializers.user import (
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegisterSerializer,
)

User = get_user_model()


class UserRegisterView(generics.CreateAPIView):
    """用户注册视图"""

    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
            }
            return success_response(data=data)
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                error_data = {"errors": e.detail}
            return error_response(code=400, message="注册失败", data=error_data)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户个人信息视图"""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # 如果是swagger文档生成，返回默认序列化器
        if getattr(self, "swagger_fake_view", False):
            return UserProfileSerializer

        # 正常的序列化器选择逻辑
        if self.request.method in ["PUT", "PATCH"]:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
                "avatar": user.avatar.url
                if user.avatar and hasattr(user.avatar, "url")
                else settings.DEFAULT_AVATAR_URL,
                "bio": user.bio,
            }
            return success_response(data=data)
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                error_data = {"errors": e.detail}
            return error_response(code=400, message="更新失败", data=error_data)


class PasswordChangeView(generics.GenericAPIView):
    """密码修改视图"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def put(self, request, *args, **kwargs):
        """修改密码"""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            new_password = serializer.validated_data["new_password"]

            # 验证新密码
            validate_password(new_password, request.user)

            # 设置新密码
            user = request.user
            user.set_password(new_password)
            user.save()

            return success_response(message="密码修改成功")
        except serializers.ValidationError as e:
            # 序列化器验证错误，返回具体的验证错误信息
            return error_response(code=400, message="密码修改失败", data=e.detail)
        except Exception as e:
            # 其他错误（如密码验证错误），返回通用错误消息
            # 记录详细错误信息到日志，但不返回给用户
            logger = logging.getLogger(__name__)
            logger.error(f"Password change error: {str(e)}", exc_info=True)
            return error_response(code=400, message="密码修改失败，请检查输入是否符合要求")
