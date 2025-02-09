from django.urls import path

from apps.core.views.statistics import (
    ContentStatisticsView,
    UserStatisticsView,
    VisitStatisticsView,
)

urlpatterns = [
    path("visits/", VisitStatisticsView.as_view(), name="visit-statistics"),
    path("users/", UserStatisticsView.as_view(), name="user-statistics"),
    path("content/", ContentStatisticsView.as_view(), name="content-statistics"),
]
