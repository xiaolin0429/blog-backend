from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""

    list_display = [
        "id",
        "username",
        "email",
        "nickname",
        "is_staff",
        "is_active",
        "date_joined",
    ]
    list_filter = ["is_staff", "is_active"]
    search_fields = ["username", "email", "nickname"]
    ordering = ["-date_joined"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("个人信息", {"fields": ("nickname", "avatar", "bio")}),
    )
