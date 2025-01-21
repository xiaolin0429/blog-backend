from django.urls import path
from ..views.auth import (
    LoginView,
    LogoutView,
    TokenRefreshView,
    PasswordChangeView
)

app_name = 'auth'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
] 