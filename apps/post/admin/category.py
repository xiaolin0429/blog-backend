from django.contrib import admin

from ..models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """分类管理"""

    list_display = [
        "id",
        "name",
        "description",
        "parent",
        "order",
        "created_at",
        "updated_at",
    ]
    list_filter = ["parent"]
    search_fields = ["name", "description"]
    ordering = ["order", "id"]
