from django.urls import path, re_path

from .views.statistics import (
    ContentStatisticsView,
    UserStatisticsView,
    VisitStatisticsView,
)
from .views.storage import (
    FileContentView,
    FileDeleteView,
    FileListView,
    FileRenameView,
    FileUploadView,
)

app_name = "core"

# 文件管理相关的URL
storage_urlpatterns = [
    path("upload", FileUploadView.as_view(), name="file-upload"),
    path("files/<str:file_id>", FileDeleteView.as_view(), name="file-delete"),
    path("files", FileListView.as_view(), name="file-list"),
    path("files/<str:file_id>/rename", FileRenameView.as_view(), name="file-rename"),
    path("files/<str:file_id>/content", FileContentView.as_view(), name="file-content"),
]

# 统计相关的URL
statistics_urlpatterns = [
    path("statistics/visits", VisitStatisticsView.as_view(), name="visit-statistics"),
    path("statistics/users", UserStatisticsView.as_view(), name="user-statistics"),
    path(
        "statistics/content", ContentStatisticsView.as_view(), name="content-statistics"
    ),
]

urlpatterns = storage_urlpatterns + statistics_urlpatterns
