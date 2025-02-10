from django.urls import path

from . import views

app_name = "overview"

urlpatterns = [
    path("", views.system_overview, name="overview"),
    path("system/", views.system_info, name="system"),
    path("content/", views.content_stats, name="content"),
    path("storage/", views.storage_stats, name="storage"),
]
