from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

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
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return success_response(message="密码修改成功")
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                error_data = {"errors": e.detail}
            return error_response(code=400, message="密码修改失败", data=error_data)
