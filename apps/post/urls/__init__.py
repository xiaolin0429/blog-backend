from django.urls import include, path

from ..views import (
    PostEmptyTrashView,
    PostPermanentDeleteView,
    PostRestoreView,
    PostTrashListView,
)

app_name = "post"

urlpatterns = [
    path("posts/", include("apps.post.urls.post")),
    path("categories/", include("apps.post.urls.category")),
    path("tags/", include("apps.post.urls.tag")),
    path("comments/", include("apps.post.urls.comment")),
    path("search/", include("apps.post.urls.search")),
    # 回收站相关路由
    path("trash/posts/empty/", PostEmptyTrashView.as_view(), name="post_empty_trash"),
    path(
        "trash/posts/<int:pk>/restore/", PostRestoreView.as_view(), name="post_restore"
    ),
    path(
        "trash/posts/<int:pk>/",
        PostPermanentDeleteView.as_view(),
        name="post_permanent_delete",
    ),
    path("trash/posts/", PostTrashListView.as_view(), name="post_trash_list"),
]
