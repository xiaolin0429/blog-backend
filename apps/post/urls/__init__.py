from django.urls import path, include

app_name = 'post'

urlpatterns = [
    path('', include('apps.post.urls.post')),
] 