from django.urls import path

from ..views.comment import (
    CommentDetailView,
    CommentListCreateView,
    GlobalCommentListView,
)

urlpatterns = [
    # 全局评论列表
    path("", GlobalCommentListView.as_view(), name="global_comment_list"),
    # 文章评论列表和创建
    path(
        "posts/<int:post_id>/",
        CommentListCreateView.as_view(),
        name="comment_list_create",
    ),
    # 评论详情、更新和删除
    path("<int:pk>/", CommentDetailView.as_view(), name="comment_detail"),
]
