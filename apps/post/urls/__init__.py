from django.urls import path, include
from ..views import (
    PostTrashListView, PostRestoreView,
    PostPermanentDeleteView, PostEmptyTrashView
)

app_name = 'post'

urlpatterns = [
    path('posts/', include('apps.post.urls.post')),
    path('', include('apps.post.urls.comment')),
    path('categories/', include('apps.post.urls.category')),
    path('tags/', include('apps.post.urls.tag')),
    
    # 回收站相关路由
    path('trash/posts/empty/', PostEmptyTrashView.as_view(), name='post_empty_trash'),
    path('trash/posts/<int:pk>/restore/', PostRestoreView.as_view(), name='post_restore'),
    path('trash/posts/<int:pk>/', PostPermanentDeleteView.as_view(), name='post_permanent_delete'),
    path('trash/posts/', PostTrashListView.as_view(), name='post_trash_list'),
] 