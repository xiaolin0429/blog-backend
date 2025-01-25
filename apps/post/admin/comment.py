from django.contrib import admin

from ..models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """评论管理"""

    list_display = [
        "id",
        "post",
        "author",
        "content",
        "parent",
        "created_at",
        "updated_at",
    ]
    list_filter = ["post", "author", "parent"]
    search_fields = ["content", "author__username", "post__title"]
    ordering = ["-created_at"]
