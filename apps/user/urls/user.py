from django.urls import path
from ..views.user import UserRegisterView, UserProfileView, PasswordChangeView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('me/', UserProfileView.as_view(), name='profile'),
    path('me/password/', PasswordChangeView.as_view(), name='password_change'),
] 