from django.core.exceptions import ValidationError
from django.http import Http404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.response import error_response, success_response

from ..models import Category
from ..serializers import CategorySerializer


class CategoryListView(generics.ListCreateAPIView):
    """分类列表视图"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_fields = ["parent"]
    search_fields = ["name", "description"]
    ordering_fields = ["order", "created_at"]
    ordering = ["order", "id"]

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        parent = self.request.query_params.get("parent")
        if parent:
            # 如果指定了父分类，只返回该父分类下的子分类
            queryset = queryset.filter(parent_id=parent)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return success_response(data=serializer.data)
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                if "name" in e.detail and any(
                    "已存在" in str(err) for err in e.detail["name"]
                ):
                    name = request.data.get("name", "")
                    return error_response(
                        code=400,
                        message="创建分类失败",
                        data={"errors": {"name": [f"分类 '{name}' 已存在"]}},
                    )
                error_data = {"errors": e.detail}
            return error_response(code=400, message="创建分类失败", data=error_data)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """分类详情视图"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return success_response(data=serializer.data)
        except Category.DoesNotExist:
            return error_response(code=404, message="分类不存在")

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return success_response(data=serializer.data)
        except (Category.DoesNotExist, Http404):
            return error_response(code=404, message="分类不存在")
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                error_data = {"errors": e.detail}
            return error_response(code=400, message="更新分类失败", data=error_data)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return error_response(
                code=204, message="success", data=None, status_code=status.HTTP_200_OK
            )
        except (Category.DoesNotExist, Http404):
            return error_response(
                code=404, message="分类不存在", status_code=status.HTTP_200_OK
            )
        except ValidationError as e:
            return error_response(
                code=422, message=str(e), status_code=status.HTTP_200_OK
            )


class CategoryQuickCreateView(APIView):
    """快速创建分类视图"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")
        parent_id = request.data.get("parent")

        if not name:
            return error_response(code=400, message="分类名称不能为空")

        # 检查名称长度
        if len(name) < 2 or len(name) > 50:
            return error_response(code=400, message="分类名称长度必须在2-50个字符之间")

        # 检查是否已存在
        if Category.objects.filter(name=name).exists():
            return error_response(code=409, message="分类名称已存在")

        # 检查父分类是否存在
        parent = None
        if parent_id:
            try:
                parent = Category.objects.get(id=parent_id)
            except Category.DoesNotExist:
                return error_response(code=404, message="父分类不存在")

        # 创建分类
        category = Category.objects.create(name=name, parent=parent)

        return success_response(
            data={
                "id": category.id,
                "name": category.name,
                "parent": parent.id if parent else None,
                "parent_name": parent.name if parent else None,
                "created_at": category.created_at.isoformat(),
            }
        )
