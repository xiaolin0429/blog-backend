from django.urls import include, path

from rest_framework.routers import DefaultRouter

from ..views.admin import UserManagementViewSet

router = DefaultRouter()
router.register("users", UserManagementViewSet, basename="user-management")

urlpatterns = [
    path("", include(router.urls)),
]
