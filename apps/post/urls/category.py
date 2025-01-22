from django.urls import path
from ..views import (
    CategoryListView, CategoryDetailView,
    CategoryQuickCreateView
)

urlpatterns = [
    # GET 获取列表，POST 创建分类
    path('', CategoryListView.as_view(), name='category_list'),
    # POST 快速创建分类（简化版）
    path('quick-create/', CategoryQuickCreateView.as_view(), name='category_quick_create'),
    # GET 获取详情，PUT/PATCH 更新分类，DELETE 删除分类
    path('<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
] 