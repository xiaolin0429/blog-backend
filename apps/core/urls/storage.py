from django.urls import path

from apps.core.views.storage import (
    FileContentView,
    FileDeleteView,
    FileListView,
    FileRenameView,
    FileUploadView,
)

urlpatterns = [
    path("upload", FileUploadView.as_view(), name="file-upload"),
    path("files/<str:file_id>", FileDeleteView.as_view(), name="file-delete"),
    path("files", FileListView.as_view(), name="file-list"),
    path("files/<str:file_id>/rename", FileRenameView.as_view(), name="file-rename"),
    path("files/<str:file_id>/content", FileContentView.as_view(), name="file-content"),
]
