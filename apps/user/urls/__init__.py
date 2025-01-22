from django.urls import path, include

app_name = 'user'

urlpatterns = [
    path('', include('apps.user.urls.user')),  # 用户相关URL
    path('auth/', include('apps.user.urls.auth')),  # 认证相关URL
] 