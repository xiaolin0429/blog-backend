from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    自定义权限类：
    - 允许所有用户进行只读操作（GET, HEAD, OPTIONS）
    - 只允许管理员进行写操作（POST, PUT, DELETE, PATCH）
    """

    def has_permission(self, request, view):
        # 允许所有用户进行只读操作
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写操作需要用户是管理员
        return bool(request.user and request.user.is_staff) 