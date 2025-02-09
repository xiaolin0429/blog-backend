from rest_framework import permissions


class IsHigherLevelUser(permissions.BasePermission):
    """
    确保操作者的权限级别高于被操作对象的自定义权限类
    """

    def has_object_permission(self, request, view, obj):
        # 如果是安全的HTTP方法（如GET），则允许访问
        if request.method in permissions.SAFE_METHODS:
            return True

        # 超级管理员可以操作任何用户
        if request.user.is_superuser:
            return True

        # 普通管理员只能操作普通用户
        if request.user.is_staff and not (obj.is_staff or obj.is_superuser):
            return True

        return False

    def has_permission(self, request, view):
        # 基础权限检查：必须是管理员
        return bool(request.user and request.user.is_staff)
