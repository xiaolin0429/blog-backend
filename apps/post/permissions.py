from rest_framework import permissions


class IsPostAuthor(permissions.BasePermission):
    """
    自定义权限类，只允许文章作者访问
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
