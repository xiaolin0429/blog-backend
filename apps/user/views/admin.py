import logging

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from rest_framework import filters, generics, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.core.response import error_response, success_response
from apps.user.permissions import IsHigherLevelUser
from apps.user.serializers.admin import (
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class UserManagementViewSet(ModelViewSet):
    """
    用户管理视图集

    提供用户的增删改查、状态修改、角色分配等功能，包含完整的权限控制
    """

    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser,
        IsHigherLevelUser,
    ]
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "nickname"]
    ordering_fields = ["id", "date_joined", "last_login"]
    ordering = ["-date_joined"]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        elif self.action == "retrieve":
            return UserDetailSerializer
        return UserListSerializer

    def perform_update(self, serializer):
        """
        执行更新操作时的处理
        """
        original_user = serializer.instance
        logger.info(
            f"User {self.request.user}(ID:{self.request.user.id}) is modifying user "
            f"{original_user}(ID:{original_user.id})"
        )
        super().perform_update(serializer)
        logger.info(
            f"User {original_user}(ID:{original_user.id}) has been updated by "
            f"{self.request.user}(ID:{self.request.user.id})"
        )

    def perform_destroy(self, instance):
        """
        执行删除操作时的处理
        """
        if instance.is_superuser:
            superuser_count = User.objects.filter(is_superuser=True).count()
            if superuser_count <= 1:
                raise PermissionError("不能删除唯一的超级管理员")

        if instance.id == self.request.user.id:
            raise PermissionError("不能删除自己的账号")

        logger.info(
            f"User {instance}(ID:{instance.id}) is being deleted by "
            f"{self.request.user}(ID:{self.request.user.id})"
        )
        super().perform_destroy(instance)

    def list(self, request, *args, **kwargs):
        """获取用户列表"""
        try:
            # 获取查询参数
            status_filter = request.query_params.get("status")
            role_filter = request.query_params.get("role")
            search_query = request.query_params.get("search")

            # 构建查询条件
            queryset = self.get_queryset()
            if status_filter:
                queryset = queryset.filter(is_active=status_filter == "active")
            if role_filter:
                if role_filter == "admin":
                    queryset = queryset.filter(is_staff=True)
                elif role_filter == "user":
                    queryset = queryset.filter(is_staff=False)
            if search_query:
                queryset = queryset.filter(
                    Q(username__icontains=search_query)
                    | Q(email__icontains=search_query)
                    | Q(nickname__icontains=search_query)
                )

            # 分页
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return success_response(data=serializer.data)
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            return error_response(code=500, message="获取用户列表失败")

    def create(self, request, *args, **kwargs):
        """创建新用户"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return success_response(
                message="创建用户成功", data=UserDetailSerializer(user).data
            )
        except serializers.ValidationError as e:
            logger.error(f"创建用户数据验证失败: {str(e)}")
            # 处理密码相关的错误
            if "password" in e.detail:
                error_messages = []
                for error in e.detail["password"]:
                    if error.code == "password_too_common":
                        error_messages.append("密码太常见，请使用更复杂的密码")
                    elif error.code == "password_too_short":
                        error_messages.append("密码太短，请至少使用8个字符")
                    elif error.code == "password_too_similar":
                        error_messages.append("密码与用户名太相似")
                    elif error.code == "password_entirely_numeric":
                        error_messages.append("密码不能全是数字")
                    else:
                        error_messages.append(str(error))
                return error_response(
                    code=400, message="密码验证失败", data={"password": error_messages}
                )
            # 处理其他字段的错误
            return error_response(code=400, message="创建用户失败", data={"errors": e.detail})
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            return error_response(code=500, message=f"创建用户失败: {str(e)}")

    def update(self, request, *args, **kwargs):
        """更新用户信息"""
        try:
            instance = self.get_object()

            # 记录请求数据
            logger.info(f"开始处理用户更新请求 - 用户ID: {instance.id}")
            logger.debug(f"原始请求数据: {dict(request.data)}")

            # 创建一个新的数据字典，只包含要更新的字段
            update_data = {}

            # 基本字段列表（允许修改的非权限字段）
            basic_fields = ["email", "nickname", "bio", "avatar"]

            # 权限字段列表
            permission_fields = ["is_staff", "is_superuser", "is_active"]

            # 处理基本字段
            for field in basic_fields:
                if field in request.data:
                    update_data[field] = request.data[field]

            # 处理权限字段
            permission_changed = False
            permission_changes = {}  # 记录权限变更
            for field in permission_fields:
                if field in request.data:
                    new_value = request.data[field]
                    if isinstance(new_value, str):
                        new_value = new_value.lower() == "true"
                    current_value = getattr(instance, field)

                    # 只有当值真正变化时才记录变更
                    if new_value != current_value:
                        permission_changed = True
                        permission_changes[field] = {
                            "from": current_value,
                            "to": new_value,
                        }
                        update_data[field] = new_value

            # 如果没有任何字段需要更新，直接返回成功
            if not update_data:
                return success_response(
                    message="无需更新", data=UserDetailSerializer(instance).data
                )

            # 如果涉及权限变更，进行权限检查
            if permission_changed:
                # 记录权限变更详情
                logger.info(
                    f"检测到权限变更请求 - 用户: {instance.username}(ID:{instance.id}), "
                    f"变更详情: {permission_changes}"
                )

                # 不能修改自己的权限
                if instance.id == request.user.id:
                    logger.warning(
                        f"用户 {request.user.username}(ID:{request.user.id}) "
                        f"尝试修改自己的权限被拒绝"
                    )
                    return error_response(code=403, message="不能修改自己的权限")

                # 只有超级管理员可以修改权限
                if not request.user.is_superuser:
                    logger.warning(
                        f"非超级管理员 {request.user.username}(ID:{request.user.id}) "
                        f"尝试修改用户权限被拒绝"
                    )
                    return error_response(code=403, message="只有超级管理员可以修改用户权限")

                # 检查是否试图降级唯一的超级管理员
                if (
                    instance.is_superuser
                    and "is_superuser" in update_data
                    and not update_data["is_superuser"]
                ):
                    superuser_count = User.objects.filter(is_superuser=True).count()
                    if superuser_count <= 1:
                        logger.warning(
                            f"尝试降级唯一超级管理员 {instance.username}(ID:{instance.id}) "
                            f"的操作被拒绝"
                        )
                        return error_response(code=403, message="系统必须保留至少一个超级管理员")

                # 如果取消超级管理员权限，同时也要取消管理员权限
                if "is_superuser" in update_data and not update_data["is_superuser"]:
                    update_data["is_staff"] = False
                    permission_changes["is_staff"] = {
                        "from": instance.is_staff,
                        "to": False,
                    }

            # 记录处理后的更新数据
            logger.debug(f"处理后的更新数据: {update_data}")

            serializer = self.get_serializer(instance, data=update_data, partial=True)

            try:
                serializer.is_valid(raise_exception=True)
            except serializers.ValidationError as e:
                logger.error(f"数据验证失败: {str(e)}")
                return error_response(code=400, message="数据验证失败", data=e.detail)

            try:
                user = serializer.save()
                # 记录成功的更新
                if permission_changed:
                    logger.info(
                        f"用户权限更新成功 - 操作者: {request.user.username}(ID:{request.user.id}), "
                        f"目标用户: {user.username}(ID:{user.id}), "
                        f"权限变更: {permission_changes}"
                    )
                else:
                    logger.info(
                        f"用户基本信息更新成功 - 操作者: {request.user.username}(ID:{request.user.id}), "
                        f"目标用户: {user.username}(ID:{user.id}), "
                        f"更新字段: {list(update_data.keys())}"
                    )
                return success_response(
                    message="更新用户信息成功", data=UserDetailSerializer(user).data
                )
            except Exception as e:
                logger.error(f"保存用户数据失败: {str(e)}")
                return error_response(code=500, message="保存用户数据失败")

        except Exception as e:
            logger.error(f"更新用户信息失败: {str(e)}")
            return error_response(code=500, message="更新用户信息失败")

    def destroy(self, request, *args, **kwargs):
        """删除用户"""
        try:
            instance = self.get_object()

            # 检查是否是超级管理员
            if instance.is_superuser:
                superuser_count = User.objects.filter(is_superuser=True).count()
                if superuser_count <= 1:
                    logger.warning(
                        f"尝试删除唯一超级管理员 {instance.username}(ID:{instance.id}) " f"的操作被拒绝"
                    )
                    return error_response(code=403, message="不能删除唯一的超级管理员")

            # 检查是否是自己
            if instance.id == request.user.id:
                logger.warning(
                    f"用户 {request.user.username}(ID:{request.user.id}) " f"尝试删除自己的账号被拒绝"
                )
                return error_response(code=403, message="不能删除自己的账号")

            # 执行软删除：将用户设置为非活跃
            instance.is_active = False
            instance.save()

            # 记录操作日志
            logger.info(
                f"用户 {instance.username}(ID:{instance.id}) 已被 "
                f"{request.user.username}(ID:{request.user.id}) 删除（软删除）"
            )

            return success_response(
                message="删除用户成功", data=UserDetailSerializer(instance).data
            )

        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            return error_response(code=500, message="删除用户失败，请稍后重试")

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """激活用户"""
        try:
            user = self.get_object()

            # 检查用户状态
            if user.is_active:
                return error_response(code=400, message="用户已经是激活状态")

            # 执行激活操作
            user.is_active = True
            user.save()

            # 记录操作日志
            logger.info(
                f"用户 {user.username}(ID:{user.id}) 已被 "
                f"{request.user.username}(ID:{request.user.id}) 激活"
            )

            return success_response(
                message="激活用户成功", data=UserDetailSerializer(user).data
            )

        except Exception as e:
            logger.error(f"激活用户失败: {str(e)}")
            return error_response(code=500, message="激活用户失败，请稍后重试")

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """停用用户"""
        try:
            user = self.get_object()

            # 检查是否是超级管理员
            if user.is_superuser:
                superuser_count = User.objects.filter(is_superuser=True).count()
                if superuser_count <= 1:
                    logger.warning(
                        f"尝试停用唯一超级管理员 {user.username}(ID:{user.id}) " f"的操作被拒绝"
                    )
                    return error_response(code=403, message="不能停用唯一的超级管理员")

            # 检查是否是自己
            if user.id == request.user.id:
                logger.warning(
                    f"用户 {request.user.username}(ID:{request.user.id}) " f"尝试停用自己的账号被拒绝"
                )
                return error_response(code=403, message="不能停用自己的账号")

            # 检查用户状态
            if not user.is_active:
                return error_response(code=400, message="用户已经是停用状态")

            # 执行停用操作
            user.is_active = False
            user.save()

            # 记录操作日志
            logger.info(
                f"用户 {user.username}(ID:{user.id}) 已被 "
                f"{request.user.username}(ID:{request.user.id}) 停用"
            )

            return success_response(
                message="停用用户成功", data=UserDetailSerializer(user).data
            )

        except Exception as e:
            logger.error(f"停用用户失败: {str(e)}")
            return error_response(code=500, message="停用用户失败，请稍后重试")

    @action(detail=True, methods=["post"])
    def set_admin(self, request, pk=None):
        """设置管理员权限"""
        try:
            user = self.get_object()
            user.is_staff = True
            user.save()
            return success_response(message="设置管理员权限成功")
        except Exception as e:
            logger.error(f"设置管理员权限失败: {str(e)}")
            return error_response(code=500, message="设置管理员权限失败")

    @action(detail=True, methods=["post"])
    def remove_admin(self, request, pk=None):
        """移除管理员权限"""
        try:
            user = self.get_object()
            user.is_staff = False
            user.save()
            return success_response(message="移除管理员权限成功")
        except Exception as e:
            logger.error(f"移除管理员权限失败: {str(e)}")
            return error_response(code=500, message="移除管理员权限失败")

    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        """重置用户密码"""
        try:
            user = self.get_object()
            new_password = request.data.get("new_password")
            if not new_password:
                return error_response(code=400, message="新密码不能为空")

            user.set_password(new_password)
            user.save()
            return success_response(message="重置密码成功")
        except Exception as e:
            logger.error(f"重置密码失败: {str(e)}")
            return error_response(code=500, message="重置密码失败")
