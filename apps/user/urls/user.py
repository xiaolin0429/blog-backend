from django.urls import path
from ..views.user import UserRegisterView, UserProfileView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('me/', UserProfileView.as_view(), name='profile'),
] 