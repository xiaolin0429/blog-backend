from django.contrib import admin

from ..models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """文章管理"""

    list_display = [
        "id",
        "title",
        "author",
        "category",
        "status",
        "views",
        "likes",
        "created_at",
        "published_at",
    ]
    list_filter = ["status", "category", "author", "tags"]
    search_fields = ["title", "content", "excerpt", "author__username"]
    filter_horizontal = ["tags"]
    ordering = ["-created_at"]
    readonly_fields = ["views", "likes", "created_at", "updated_at", "published_at"]
