from django.urls import path

from .views.storage import FileDeleteView, FileListView, FileRenameView, FileUploadView

app_name = "core"

urlpatterns = [
    # Add core URLs here
    # 文件管理
    path("upload", FileUploadView.as_view(), name="file-upload"),
    path("upload/<path:path>", FileDeleteView.as_view(), name="file-delete"),
    path("files", FileListView.as_view(), name="file-list"),
    path("files/<path:path>/rename", FileRenameView.as_view(), name="file-rename"),
]
