from django.urls import path, include

app_name = 'post'

urlpatterns = [
    path('posts/', include('apps.post.urls.post')),
    path('', include('apps.post.urls.comment')),
    path('categories/', include('apps.post.urls.category')),
    path('tags/', include('apps.post.urls.tag')),
] 