from django.urls import path

from apps.core.views.statistics import UserStatisticsView, VisitStatisticsView

urlpatterns = [
    path("statistics/visits/", VisitStatisticsView.as_view(), name="visit-statistics"),
    path("statistics/users/", UserStatisticsView.as_view(), name="user-statistics"),
]
