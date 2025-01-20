from django.urls import path
from ..views import (
    PostListView, PostDetailView,
    PostUpdateView, PostDeleteView, PostLikeView,
    PostViewView, PostArchiveView, PostTrashListView,
    PostRestoreView, PostPermanentDeleteView, PostEmptyTrashView
)

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('<int:pk>/like/', PostLikeView.as_view(), name='post_like'),
    path('<int:pk>/view/', PostViewView.as_view(), name='post_view'),
    path('<int:pk>/archive/', PostArchiveView.as_view(), name='post_archive'),
    
    # 回收站相关路由
    path('trash/', PostTrashListView.as_view(), name='post_trash_list'),
    path('trash/<int:pk>/restore/', PostRestoreView.as_view(), name='post_restore'),
    path('trash/<int:pk>/', PostPermanentDeleteView.as_view(), name='post_permanent_delete'),
    path('trash/empty/', PostEmptyTrashView.as_view(), name='post_empty_trash'),
] 