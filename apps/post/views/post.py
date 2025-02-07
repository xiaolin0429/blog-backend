import logging
from datetime import timedelta

from django.db import DatabaseError
from django.db.models import Q
from django.utils import timezone

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, pagination, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle

from apps.core.response import error_response, success_response

from ..models import Post
from ..permissions import IsPostAuthor
from ..serializers import (
    PostAutoSaveResponseSerializer,
    PostAutoSaveSerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer,
)

# 创建日志记录器
logger = logging.getLogger(__name__)


class PostPagination(pagination.PageNumberPagination):
    """文章分页类"""

    page_size = 10
    page_size_query_param = "size"
    max_page_size = 50


class PostListView(generics.ListCreateAPIView):
    """文章列表视图"""

    serializer_class = PostListSerializer
    filterset_fields = ["category", "tags", "status", "author"]
    search_fields = ["title", "content", "excerpt"]
    ordering_fields = ["created_at", "updated_at", "published_at", "views", "likes"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated()]

    @swagger_auto_schema(
        operation_summary="获取文章列表",
        operation_description="获取所有文章列表，支持分页、过滤、搜索和排序。普通用户只能看到已发布的文章，管理员可以看到所有文章。",
        manual_parameters=[
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="按分类ID过滤",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "tags",
                openapi.IN_QUERY,
                description="按标签ID过滤，可多选",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="按状态过滤（draft-草稿，published-已发布，archived-已归档）",
                type=openapi.TYPE_STRING,
                enum=["draft", "published", "archived"],
                required=False,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="搜索关键词（标题、内容、摘要）",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="排序字段（前缀-表示降序）",
                type=openapi.TYPE_STRING,
                enum=[
                    "created_at",
                    "-created_at",
                    "updated_at",
                    "-updated_at",
                    "published_at",
                    "-published_at",
                    "views",
                    "-views",
                    "likes",
                    "-likes",
                ],
                required=False,
            ),
        ],
        responses={200: PostListSerializer(many=True), 401: "未认证"},
    )
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return success_response(
                data=self.paginator.get_paginated_response(serializer.data).data
            )
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data={"results": serializer.data, "count": queryset.count()}
        )

    @swagger_auto_schema(
        operation_summary="创建新文章",
        operation_description="创建一篇新文章，需要认证。作者会自动设置为当前登录用户。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "content"],
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="文章标题", max_length=200
                ),
                "content": openapi.Schema(type=openapi.TYPE_STRING, description="文章内容"),
                "excerpt": openapi.Schema(
                    type=openapi.TYPE_STRING, description="文章摘要（可选）"
                ),
                "category": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="分类ID（可选）"
                ),
                "tags": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description="标签ID列表（可选）",
                ),
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="文章状态（可选，默认为draft）",
                    enum=["draft", "published", "archived"],
                ),
            },
        ),
        responses={201: PostCreateUpdateSerializer, 400: "参数错误", 401: "未认证"},
    )
    def post(self, request, *args, **kwargs):
        logger.info(f"接收到创建文章请求，数据: {request.data}")
        serializer = self.get_serializer(data=request.data)
        try:
            logger.info("开始验证数据")
            serializer.is_valid(raise_exception=True)
            logger.info("数据验证通过，开始创建文章")
            self.perform_create(serializer)
            logger.info("文章创建成功")
            return success_response(data=serializer.data)
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                error_data = {"errors": e.detail}
            logger.error(f"创建文章失败: {str(e)}, 错误详情: {error_data}")
            return error_response(code=400, message="创建文章失败", data=error_data)

    def get_queryset(self):
        # 如果是swagger文档生成，返回空查询集
        if getattr(self, "swagger_fake_view", False):
            return Post.objects.none()

        # 正常的查询逻辑
        queryset = Post.objects.filter(is_deleted=False)

        # 如果不是管理员或未登录用户,只能看到已发布的文章
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            queryset = queryset.filter(status="published")

        # 应用过滤器
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)

        tags = self.request.query_params.getlist("tags")
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(content__icontains=search)
                | Q(excerpt__icontains=search)
            ).distinct()

        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateUpdateSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostCreateView(generics.CreateAPIView):
    """文章创建视图"""

    serializer_class = PostCreateUpdateSerializer
    permission_classes = [IsAuthenticated]


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """文章详情视图"""

    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def get_queryset(self):
        # 如果是swagger文档生成，返回空查询集
        if getattr(self, "swagger_fake_view", False):
            return Post.objects.none()

        # 正常的查询逻辑
        if self.request.method in ["DELETE", "PUT", "PATCH"]:
            return Post.objects.filter(author=self.request.user)
        elif self.request.user.is_staff:
            return Post.objects.all()
        return Post.objects.filter(status="published")

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return success_response(data=serializer.data)
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                error_data = {"errors": e.detail}
            return error_response(code=404, message="文章不存在或无权限访问", data=error_data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return success_response(data=serializer.data)
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                error_data = {"errors": e.detail}
            return error_response(code=400, message="更新文章失败", data=error_data)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.deleted_at = timezone.now()
            instance.save()
            return success_response(message="文章已移至回收站")
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                error_data = {"errors": e.detail}
            return error_response(code=404, message="文章不存在或无权限删除", data=error_data)


class PostUpdateView(generics.UpdateAPIView):
    """文章更新视图"""

    queryset = Post.objects.all()
    serializer_class = PostCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 如果是swagger文档生成，返回空查询集
        if getattr(self, "swagger_fake_view", False):
            return Post.objects.none()
        return Post.objects.filter(author=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return success_response(data=serializer.data)
        except Exception as e:
            error_data = None
            if hasattr(e, "detail"):
                error_data = {"errors": e.detail}
            return error_response(code=400, message="更新文章失败", data=error_data)

    def perform_update(self, serializer):
        serializer.save()


class PostLikeView(views.APIView):
    """文章点赞视图"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, status="published", is_deleted=False)
            post.likes += 1
            post.save()
            return success_response(data={"likes": post.likes})
        except Post.DoesNotExist:
            return error_response(code=404, message="文章不存在或未发布")


class PostViewView(views.APIView):
    """文章浏览视图"""

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, status="published", is_deleted=False)
            post.views += 1
            post.save()
            return success_response(data={"views": post.views})
        except Post.DoesNotExist:
            return error_response(code=404, message="文章不存在或未发布")


class PostArchiveView(views.APIView):
    """文章归档视图"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
            post.status = "archived"
            post.save()
            return success_response(data={"status": "archived"})
        except Post.DoesNotExist:
            return error_response(code=404, message="文章不存在或无权限")


class PostTrashListView(generics.ListAPIView):
    """回收站文章列表视图"""

    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["title", "content", "excerpt"]
    ordering_fields = ["deleted_at"]
    ordering = ["-deleted_at"]
    pagination_class = PostPagination

    def get_queryset(self):
        if self.request.user.is_staff:
            return Post.objects.filter(is_deleted=True)
        return Post.objects.filter(is_deleted=True, author=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return success_response(
                data=self.paginator.get_paginated_response(serializer.data).data
            )
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data={"results": serializer.data, "count": queryset.count()}
        )


class PostRestoreView(views.APIView):
    """恢复已删除文章视图"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, is_deleted=True)
            # 检查权限
            if not request.user.is_staff and post.author != request.user:
                return success_response(code=404, message="文章不存在或无权限操作")

            post.restore()
            return success_response(
                data={"id": post.id, "title": post.title, "status": post.status}
            )
        except Post.DoesNotExist:
            return success_response(code=404, message="文章不存在或无权限操作")


class PostPermanentDeleteView(views.APIView):
    """永久删除文章视图"""

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, is_deleted=True)
            # 检查权限
            if not request.user.is_staff and post.author != request.user:
                return success_response(code=404, message="文章不存在或无权限操作")

            post.delete()
            return success_response(code=204, message="success", data=None)
        except Post.DoesNotExist:
            return success_response(code=404, message="文章不存在或无权限操作")


class PostEmptyTrashView(views.APIView):
    """清空回收站视图"""

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            # 只删除当前用户的文章，管理员可以删除所有文章
            queryset = Post.objects.filter(is_deleted=True)
            if not request.user.is_staff:
                queryset = queryset.filter(author=request.user)

            deleted_count = queryset.count()
            queryset.delete()

            return success_response(
                code=204, message="success", data={"deleted_count": deleted_count}
            )
        except Exception as e:
            return success_response(code=400, message="清空回收站失败")


class PostAutoSaveThrottle(ScopedRateThrottle):
    """自定义限流类，支持动态调整保存间隔"""

    scope = "post_auto_save"

    def allow_request(self, request, view):
        if request.method != "POST":
            return True

        # 获取上次保存时间
        post = view.get_object()
        if not post:
            return False

        # 如果是强制保存，允许请求
        if request.data.get("force_save", False):
            return True

        last_save_time = None
        if post.auto_save_content and "auto_save_time" in post.auto_save_content:
            try:
                last_save_time = timezone.datetime.fromisoformat(
                    post.auto_save_content["auto_save_time"]
                )
            except (ValueError, TypeError):
                pass

        if last_save_time:
            # 计算距离上次保存的时间间隔
            time_since_last_save = timezone.now() - last_save_time

            # 如果间隔小于最小保存间隔（10秒），拒绝请求
            if time_since_last_save < timedelta(seconds=10):
                return False

        # 调用父类的限流检查
        return super().allow_request(request, view)

    def wait(self):
        """返回需要等待的时间"""
        return None


class PostAutoSaveView(views.APIView):
    """文章自动保存视图"""

    permission_classes = [IsAuthenticated, IsPostAuthor]
    throttle_classes = [PostAutoSaveThrottle]

    def get_object(self):
        """获取文章对象"""
        try:
            obj = Post.objects.get(pk=self.kwargs["pk"], is_deleted=False)
            self.check_object_permissions(self.request, obj)
            return obj
        except Post.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="自动保存文章",
        operation_description="自动保存文章的内容。每10秒最多保存一次，每2分钟强制保存一次。",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="文章标题"),
                "content": openapi.Schema(type=openapi.TYPE_STRING, description="文章内容"),
                "excerpt": openapi.Schema(type=openapi.TYPE_STRING, description="文章摘要"),
                "category": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="分类ID"
                ),
                "tags": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description="标签ID列表",
                ),
                "force_save": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, description="是否强制保存（距离上次保存超过2分钟时）"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="自动保存成功",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="状态码"
                        ),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, description="提示信息"
                        ),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "version": openapi.Schema(
                                    type=openapi.TYPE_INTEGER, description="当前版本号"
                                ),
                                "next_save_time": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format="date-time",
                                    description="下次允许保存的时间",
                                ),
                            },
                        ),
                    },
                ),
            ),
            400: "参数错误",
            401: "未认证",
            403: "无权限",
            404: "文章不存在",
            429: "请求过于频繁",
            500: "数据库错误",
        },
    )
    def post(self, request, pk):
        """自动保存文章"""
        post = self.get_object()
        if not post:
            return error_response(code=404, message="文章不存在或无权限")

        try:
            # 获取上次保存时间
            last_save_time = None
            if post.auto_save_content and "auto_save_time" in post.auto_save_content:
                try:
                    last_save_time = timezone.datetime.fromisoformat(
                        post.auto_save_content["auto_save_time"]
                    )
                except (ValueError, TypeError):
                    pass

            # 检查是否需要强制保存
            force_save = request.data.get("force_save", False)
            if last_save_time:
                time_since_last_save = timezone.now() - last_save_time
                if time_since_last_save < timedelta(seconds=10) and not force_save:
                    next_save_time = last_save_time + timedelta(seconds=10)
                    return error_response(
                        code=429,
                        message="请求过于频繁",
                        data={"next_save_time": next_save_time.isoformat()},
                    )

            serializer = PostAutoSaveSerializer(post, data=request.data)
            if serializer.is_valid():
                post = serializer.save()
                next_save_time = timezone.now() + timedelta(seconds=10)
                return success_response(
                    data={
                        "version": post.version,
                        "next_save_time": next_save_time.isoformat(),
                    }
                )
            return error_response(code=400, message=serializer.errors)

        except DatabaseError:
            return error_response(code=500, message="数据库错误")

    @swagger_auto_schema(
        operation_summary="获取自动保存的内容",
        operation_description="获取文章最近一次自动保存的内容。如果没有自动保存内容，则返回当前内容。",
        responses={
            200: openapi.Response(
                description="获取成功",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(
                            type=openapi.TYPE_INTEGER, description="状态码"
                        ),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, description="提示信息"
                        ),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "title": openapi.Schema(
                                    type=openapi.TYPE_STRING, description="文章标题"
                                ),
                                "content": openapi.Schema(
                                    type=openapi.TYPE_STRING, description="文章内容"
                                ),
                                "excerpt": openapi.Schema(
                                    type=openapi.TYPE_STRING, description="文章摘要"
                                ),
                                "category": openapi.Schema(
                                    type=openapi.TYPE_INTEGER, description="分类ID"
                                ),
                                "tags": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                                    description="标签ID列表",
                                ),
                                "version": openapi.Schema(
                                    type=openapi.TYPE_INTEGER, description="版本号"
                                ),
                                "auto_save_time": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format="date-time",
                                    description="自动保存时间",
                                ),
                            },
                        ),
                    },
                ),
            ),
            401: "未认证",
            403: "无权限",
            404: "文章不存在",
        },
    )
    def get(self, request, pk):
        """获取自动保存的内容"""
        post = self.get_object()
        if not post:
            return error_response(code=404, message="文章不存在或无权限")

        # 如果没有自动保存内容，返回当前内容
        if not post.auto_save_content:
            data = {
                "title": post.title,
                "content": post.content,
                "excerpt": post.excerpt,
                "category": post.category_id if post.category else None,
                "tags": list(post.tags.values_list("id", flat=True)),
                "version": post.version,
                "auto_save_time": None,
            }
        else:
            serializer = PostAutoSaveResponseSerializer(post)
            data = serializer.data

        return success_response(data=data)
