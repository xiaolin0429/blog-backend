from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import BackupConfigViewSet, BackupViewSet

app_name = "backup"

router = DefaultRouter()
router.register("backups", BackupViewSet, basename="backup")
router.register("configs", BackupConfigViewSet, basename="backup-config")

urlpatterns = [
    path("", include(router.urls)),
]
