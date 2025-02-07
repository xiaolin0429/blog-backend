from django.urls import path

from ..views.post import (
    PostArchiveView,
    PostAutoSaveView,
    PostDetailView,
    PostLikeView,
    PostListView,
    PostViewView,
)

urlpatterns = [
    # 基本操作
    path("", PostListView.as_view(), name="post_list"),
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    # 互动
    path("<int:pk>/like/", PostLikeView.as_view(), name="post_like"),
    path("<int:pk>/view/", PostViewView.as_view(), name="post_view"),
    path("<int:pk>/archive/", PostArchiveView.as_view(), name="post_archive"),
    # 自动保存
    path("<int:pk>/auto-save/", PostAutoSaveView.as_view(), name="post_auto_save"),
]
