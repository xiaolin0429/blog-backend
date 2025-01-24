from django.urls import path
from ..views.search import SearchView, SearchSuggestView

urlpatterns = [
    path('', SearchView.as_view(), name='search'),
    path('suggest/', SearchSuggestView.as_view(), name='search_suggest'),
] 