from django.contrib import admin

from ..models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """标签管理"""

    list_display = ["id", "name", "created_at"]
    search_fields = ["name"]
    ordering = ["id"]
