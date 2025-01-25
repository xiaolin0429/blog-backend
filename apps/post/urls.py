from django.urls import path

from .views.post import (
    PostArchiveView,
    PostAutoSaveView,
    PostDeleteView,
    PostDetailView,
    PostEmptyTrashView,
    PostLikeView,
    PostListView,
    PostPermanentDeleteView,
    PostRestoreView,
    PostTrashListView,
    PostUpdateView,
    PostViewView,
)

app_name = "post"

urlpatterns = [
    # 文章基本操作
    path("posts/", PostListView.as_view(), name="post-list"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:pk>/update/", PostUpdateView.as_view(), name="post-update"),
    path("posts/<int:pk>/delete/", PostDeleteView.as_view(), name="post-delete"),
    # 文章互动
    path("posts/<int:pk>/like/", PostLikeView.as_view(), name="post-like"),
    path("posts/<int:pk>/view/", PostViewView.as_view(), name="post-view"),
    path("posts/<int:pk>/archive/", PostArchiveView.as_view(), name="post-archive"),
    # 回收站操作
    path("posts/trash/", PostTrashListView.as_view(), name="post-trash-list"),
    path("posts/<int:pk>/restore/", PostRestoreView.as_view(), name="post-restore"),
    path(
        "posts/<int:pk>/permanent-delete/",
        PostPermanentDeleteView.as_view(),
        name="post-permanent-delete",
    ),
    path("posts/empty-trash/", PostEmptyTrashView.as_view(), name="post-empty-trash"),
    # 自动保存
    path(
        "posts/<int:pk>/auto-save/", PostAutoSaveView.as_view(), name="post-auto-save"
    ),
]
