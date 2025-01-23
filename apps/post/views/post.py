from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from apps.core.response import success_response, error_response
from ..models import Post
from ..serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer
)

class PostListView(generics.ListCreateAPIView):
    """文章列表视图"""
    serializer_class = PostListSerializer
    filterset_fields = ['category', 'tags', 'status', 'author']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'updated_at', 'published_at', 'views', 'likes']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated()]

    @swagger_auto_schema(
        operation_summary='获取文章列表',
        operation_description='获取所有文章列表，支持分页、过滤、搜索和排序。普通用户只能看到已发布的文章，管理员可以看到所有文章。',
        manual_parameters=[
            openapi.Parameter(
                'category', openapi.IN_QUERY,
                description='按分类ID过滤',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'tags', openapi.IN_QUERY,
                description='按标签ID过滤，可多选',
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                required=False
            ),
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description='按状态过滤（draft-草稿，published-已发布，archived-已归档）',
                type=openapi.TYPE_STRING,
                enum=['draft', 'published', 'archived'],
                required=False
            ),
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description='搜索关键词（标题、内容、摘要）',
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY,
                description='排序字段（前缀-表示降序）',
                type=openapi.TYPE_STRING,
                enum=['created_at', '-created_at', 'updated_at', '-updated_at',
                      'published_at', '-published_at', 'views', '-views',
                      'likes', '-likes'],
                required=False
            )
        ],
        responses={
            200: PostListSerializer(many=True),
            401: '未认证'
        }
    )
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return success_response(data=self.paginator.get_paginated_response(serializer.data).data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data={'results': serializer.data, 'count': queryset.count()})

    @swagger_auto_schema(
        operation_summary='创建新文章',
        operation_description='创建一篇新文章，需要认证。作者会自动设置为当前登录用户。',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['title', 'content'],
            properties={
                'title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='文章标题',
                    max_length=200
                ),
                'content': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='文章内容'
                ),
                'excerpt': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='文章摘要（可选）'
                ),
                'category': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='分类ID（可选）'
                ),
                'tags': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description='标签ID列表（可选）'
                ),
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='文章状态（可选，默认为draft）',
                    enum=['draft', 'published', 'archived']
                )
            }
        ),
        responses={
            201: PostCreateUpdateSerializer,
            400: '参数错误',
            401: '未认证'
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return success_response(data=serializer.data)
        except Exception as e:
            error_data = None
            if hasattr(e, 'detail'):
                error_data = {"errors": e.detail}
            return error_response(
                code=400,
                message="创建文章失败",
                data=error_data
            )

    def get_queryset(self):
        # 如果是swagger文档生成，返回空查询集
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
            
        # 正常的查询逻辑
        queryset = Post.objects.filter(is_deleted=False)
        
        # 如果不是管理员或未登录用户,只能看到已发布的文章
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
            
        # 应用过滤器
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()
            
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(excerpt__icontains=search)
            ).distinct()
            
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostCreateView(generics.CreateAPIView):
    """文章创建视图"""
    serializer_class = PostCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

class PostDetailView(generics.RetrieveAPIView):
    """文章详情视图"""
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer

    def get_queryset(self):
        # 如果是swagger文档生成，返回空查询集
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
            
        # 正常的查询逻辑
        if self.request.user.is_staff:
            return Post.objects.all()
        return Post.objects.filter(status='published')

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return success_response(data=serializer.data)
        except Exception as e:
            error_data = None
            if hasattr(e, 'detail'):
                error_data = {"errors": e.detail}
            return error_response(
                code=404,
                message="文章不存在或无权限访问",
                data=error_data
            )

class PostUpdateView(generics.UpdateAPIView):
    """文章更新视图"""
    queryset = Post.objects.all()
    serializer_class = PostCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 如果是swagger文档生成，返回空查询集
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
        return Post.objects.filter(author=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return success_response(data=serializer.data)
        except Exception as e:
            error_data = None
            if hasattr(e, 'detail'):
                error_data = {"errors": e.detail}
            return error_response(
                code=400,
                message="更新文章失败",
                data=error_data
            )

    def perform_update(self, serializer):
        serializer.save()

class PostDeleteView(generics.DestroyAPIView):
    """文章删除视图"""
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 如果是swagger文档生成，返回空查询集
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
        return Post.objects.filter(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return success_response(message="文章已移至回收站")
        except Exception as e:
            error_data = None
            if hasattr(e, 'detail'):
                error_data = {"errors": e.detail}
            return error_response(
                code=404,
                message="文章不存在或无权限删除",
                data=error_data
            )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()

class PostLikeView(views.APIView):
    """文章点赞视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, status='published', is_deleted=False)
            post.likes += 1
            post.save()
            return success_response(data={'likes': post.likes})
        except Post.DoesNotExist:
            return error_response(
                code=404,
                message='文章不存在或未发布'
            )

class PostViewView(views.APIView):
    """文章浏览视图"""
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, status='published', is_deleted=False)
            post.views += 1
            post.save()
            return success_response(data={'views': post.views})
        except Post.DoesNotExist:
            return error_response(
                code=404,
                message='文章不存在或未发布'
            )

class PostArchiveView(views.APIView):
    """文章归档视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
            post.status = 'archived'
            post.save()
            return success_response(data={'status': 'archived'})
        except Post.DoesNotExist:
            return error_response(
                code=404,
                message='文章不存在或无权限'
            )

class PostTrashListView(generics.ListAPIView):
    """回收站文章列表视图"""
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['deleted_at']
    ordering = ['-deleted_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Post.objects.filter(is_deleted=True)
        return Post.objects.filter(is_deleted=True, author=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return success_response(data=serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)

class PostRestoreView(views.APIView):
    """恢复已删除文章视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, is_deleted=True, author=request.user)
            post.is_deleted = False
            post.status = 'draft'
            post.save()
            return success_response(data={'status': 'restored'})
        except Post.DoesNotExist:
            return error_response(
                code=404,
                message='文章不存在或无权限'
            )

class PostPermanentDeleteView(views.APIView):
    """永久删除文章视图"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, is_deleted=True, author=request.user)
            post.delete()
            return success_response(message="文章已永久删除")
        except Post.DoesNotExist:
            return error_response(
                code=404,
                message='文章不存在或无权限'
            )

class PostEmptyTrashView(views.APIView):
    """清空回收站视图"""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            # 只删除当前用户的文章
            deleted_count = Post.objects.filter(is_deleted=True, author=request.user).count()
            Post.objects.filter(is_deleted=True, author=request.user).delete()
            return success_response(
                message="回收站已清空",
                data={"deleted_count": deleted_count}
            )
        except Exception as e:
            return error_response(
                code=400,
                message="清空回收站失败",
                data={"error": str(e)}
            ) 