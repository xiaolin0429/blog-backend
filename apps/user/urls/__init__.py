from django.urls import include, path

app_name = "user"

urlpatterns = [
    path("", include("apps.user.urls.user")),  # 用户相关URL
    path("auth/", include("apps.user.urls.auth")),  # 认证相关URL
    path("admin/", include("apps.user.urls.admin")),  # 管理相关URL
]
