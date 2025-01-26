from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Max

from rest_framework import filters, generics, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.core.response import success_response

from ..models import Tag
from ..serializers import TagSerializer


class TagPagination(PageNumberPagination):
    """标签分页类"""

    page_size = 10
    page_size_query_param = "size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return {"count": self.page.paginator.count, "results": data}


class IsAuthenticatedOrReadOnly(BasePermission):
    """自定义权限类，未认证用户只能读取"""

    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        if not request.user.is_authenticated:
            raise PermissionDenied("您没有执行该操作的权限")
        return True


class TagListView(generics.ListCreateAPIView):
    """标签列表视图"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ["name"]
    ordering_fields = ["name", "id", "post_count"]
    ordering = ["id"]
    pagination_class = TagPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """重写get_queryset以支持post_count排序"""
        queryset = super().get_queryset()
        if self.request.query_params.get('ordering') in ['post_count', '-post_count']:
            # 添加post_count注解用于排序
            queryset = queryset.annotate(post_count=Count('post'))
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return success_response(
                data=self.paginator.get_paginated_response(serializer.data)
            )
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data={"results": serializer.data, "count": queryset.count()}
        )

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            # 检查标签名称是否已存在
            name = request.data.get("name")
            if name and Tag.objects.filter(name=name).exists():
                return success_response(code=409, message="标签名称已存在")
            # 进行其他验证
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return success_response(data=serializer.data)
        except serializers.ValidationError as e:
            error_data = {"errors": e.detail}
            if "name" in error_data.get("errors", {}):
                if "blank" in str(error_data["errors"]["name"]):
                    return success_response(code=400, message="标签名称不能为空")
                elif "length" in str(error_data["errors"]["name"]):
                    return success_response(code=400, message="标签名称长度必须在2-50个字符之间")
            return success_response(
                code=400,
                message="标签名称长度必须在2-50个字符之间"
                if "name" in error_data.get("errors", {})
                else "创建标签失败",
                data=error_data,
            )
        except Exception as e:
            return success_response(code=400, message=str(e))


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    """标签详情、更新和删除视图"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        """获取标签对象"""
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        try:
            return queryset.get(**filter_kwargs)
        except ObjectDoesNotExist:
            return None

    def get_serializer_context(self):
        """添加detail标记到context"""
        context = super().get_serializer_context()
        if 'request' in context and context['request'].method == 'GET':
            context['detail'] = True
        return context

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return success_response(code=404, message="标签不存在")
        serializer = self.get_serializer(instance, context={'detail': True})
        return success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return success_response(code=404, message="标签不存在")

        try:
            # 检查标签名称是否已存在
            name = request.data.get("name")
            if name and Tag.objects.filter(name=name).exclude(id=instance.id).exists():
                return success_response(code=409, message="标签名称已存在")

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return success_response(data=serializer.data)
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                error_data = {"errors": e.detail}
            return success_response(code=400, message="更新标签失败", data=error_data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return success_response(code=404, message="标签不存在")

        # 检查标签下是否存在文章
        if instance.post_set.exists():
            return success_response(code=409, message="标签下存在文章，不能删除")

        self.perform_destroy(instance)
        return success_response(message="删除成功")


class TagBatchCreateView(generics.CreateAPIView):
    """标签批量创建视图"""

    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # 检查是否有重复的标签名称
            names = [
                item.get("name") for item in request.data if isinstance(item, dict)
            ]
            if not names:
                return success_response(code=400, message="标签数据格式不正确")

            existing_names = Tag.objects.filter(name__in=names).values_list(
                "name", flat=True
            )
            if existing_names:
                return success_response(code=409, message="标签名称已存在")

            # 验证所有数据
            invalid_items = []
            for item in request.data:
                serializer = self.get_serializer(data=item)
                if not serializer.is_valid():
                    invalid_items.append(item)

            if invalid_items:
                return success_response(code=400, message="标签名称不能为空或长度不符合要求")

            # 创建标签
            created_tags = []
            for item in request.data:
                serializer = self.get_serializer(data=item)
                serializer.is_valid(raise_exception=True)
                tag = serializer.save()
                created_tags.append(serializer.data)
            
            return success_response(data=created_tags)
        except Exception as e:
            return success_response(code=400, message=str(e))


class TagStatsView(generics.GenericAPIView):
    """标签统计视图"""
    permission_classes = []

    @staticmethod
    def get(request):
        """获取标签统计信息"""
        total = Tag.objects.count()
        total_used = Tag.objects.filter(post__isnull=False).distinct().count()

        most_used = Tag.objects.annotate(
            post_count=Count('post')
        ).order_by('-post_count')[:10]

        recently_created = Tag.objects.order_by('-created_at')[:10]

        recently_used = Tag.objects.filter(
            post__isnull=False
        ).annotate(
            last_used=Max('post__created_at')
        ).order_by('-last_used')[:10]

        return success_response(data={
            'total': total,
            'total_used': total_used,
            'most_used': [{
                'id': tag.id,
                'name': tag.name,
                'post_count': tag.post_count
            } for tag in most_used],
            'recently_created': [{
                'id': tag.id,
                'name': tag.name,
                'created_at': tag.created_at
            } for tag in recently_created],
            'recently_used': [{
                'id': tag.id,
                'name': tag.name,
                'last_used_at': tag.last_used
            } for tag in recently_used]
        })
