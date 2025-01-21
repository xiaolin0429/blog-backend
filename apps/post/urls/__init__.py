from django.urls import path, include

app_name = 'post'

urlpatterns = [
    path('', include('apps.post.urls.post')),
    path('', include('apps.post.urls.comment')),
    path('', include('apps.post.urls.category')),
    path('', include('apps.post.urls.tag')),
] 