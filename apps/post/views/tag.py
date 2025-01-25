from django.core.exceptions import ObjectDoesNotExist

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
    page_size_query_param = "page_size"
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
    ordering_fields = ["name", "id"]
    ordering = ["id"]
    pagination_class = TagPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsAuthenticatedOrReadOnly]

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return success_response(code=404, message="标签不存在")
        serializer = self.get_serializer(instance)
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

            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return success_response(data=serializer.data)
        except serializers.ValidationError as e:
            error_data = {"errors": e.detail}
            return success_response(code=400, message="标签名称不符合要求", data=error_data)
        except Exception as e:
            return success_response(code=400, message=str(e))
