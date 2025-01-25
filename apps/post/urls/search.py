from django.urls import path

from ..views.search import SearchSuggestView, SearchView

urlpatterns = [
    path("", SearchView.as_view(), name="search"),
    path("suggest/", SearchSuggestView.as_view(), name="search_suggest"),
]
