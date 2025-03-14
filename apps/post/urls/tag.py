from django.urls import path

from ..views import TagBatchCreateView, TagDetailView, TagListView, TagStatsView

urlpatterns = [
    # GET 获取列表，POST 创建标签
    path("", TagListView.as_view(), name="tag_list"),
    # POST 批量创建标签
    path("batch/", TagBatchCreateView.as_view(), name="tag_batch_create"),
    # GET 获取详情，PUT 更新标签，DELETE 删除标签
    path("<int:pk>/", TagDetailView.as_view(), name="tag_detail"),
    # GET 获取标签统计信息
    path("stats/", TagStatsView.as_view(), name="tag_stats"),
]
