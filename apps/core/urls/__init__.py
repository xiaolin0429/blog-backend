from django.urls import include, path

app_name = "core"

urlpatterns = [
    path("storage/", include("apps.core.urls.storage")),  # 文件管理URLs
    path("statistics/", include("apps.core.urls.statistics")),  # 统计URLs
]
