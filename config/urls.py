"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Swagger documentation view
schema_view = get_schema_view(
    openapi.Info(
        title="个人博客系统API文档",
        default_version="v1",
        description="个人博客系统API接口文档",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@blog.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# API URL patterns
api_v1_patterns = [
    path("auth/", include("apps.user.urls.auth")),  # 直接包含认证URLs
    path("user/", include("apps.user.urls")),  # 包含用户应用的所有URLs
    path("", include("apps.post.urls", namespace="post")),  # 使用post应用的主URLs
    path("plugin/", include("apps.plugin.urls")),
    path("", include("apps.core.urls")),  # 包含core应用的所有URLs
    path("backup/", include("apps.backup.urls")),  # 包含备份应用的URLs，添加backup前缀
    path("overview/", include("apps.overview.urls")),  # 包含系统概览应用的URLs
]

urlpatterns = [
    # 根路径重定向到Swagger文档
    path("", RedirectView.as_view(url="/swagger/", permanent=False), name="index"),
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/v1/", include(api_v1_patterns)),
    # Swagger documentation
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # 调试工具
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
