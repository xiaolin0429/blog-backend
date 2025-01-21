from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
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
    permission_classes = [IsAuthenticated]

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
        return super().get(request, *args, **kwargs)

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
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        # 如果是swagger文档生成，返回空查询集
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
            
        # 正常的查询逻辑
        if self.request.user.is_staff:
            return Post.objects.all()
        return Post.objects.filter(status='published')

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

class PostDeleteView(generics.DestroyAPIView):
    """文章删除视图"""
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 如果是swagger文档生成，返回空查询集
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
        return Post.objects.filter(author=self.request.user)

class PostLikeView(views.APIView):
    """文章点赞视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, status='published')
            post.likes += 1
            post.save()
            return Response({'likes': post.likes})
        except Post.DoesNotExist:
            return Response(
                {'error': '文章不存在或未发布'},
                status=status.HTTP_404_NOT_FOUND
            )

class PostViewView(views.APIView):
    """文章浏览视图"""
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, status='published')
            post.views += 1
            post.save()
            return Response({'views': post.views})
        except Post.DoesNotExist:
            return Response(
                {'error': '文章不存在或未发布'},
                status=status.HTTP_404_NOT_FOUND
            )

class PostArchiveView(views.APIView):
    """文章归档视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
            post.status = 'archived'
            post.save()
            return Response({'status': 'archived'})
        except Post.DoesNotExist:
            return Response(
                {'error': '文章不存在或无权限'},
                status=status.HTTP_404_NOT_FOUND
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

class PostRestoreView(views.APIView):
    """恢复已删除文章视图"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='恢复已删除文章',
        operation_description='将文章从回收站恢复，状态会重置为草稿。',
        responses={
            200: openapi.Response(
                description='恢复成功',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'code': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'title': openapi.Schema(type=openapi.TYPE_STRING),
                                'status': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            ),
            404: '文章不存在或无权限'
        }
    )
    def post(self, request, pk):
        try:
            post = Post.objects.get(
                Q(author=request.user) | Q(author__is_staff=True),
                pk=pk,
                is_deleted=True
            )
            post.restore()
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'id': post.id,
                    'title': post.title,
                    'status': post.status
                }
            })
        except Post.DoesNotExist:
            return Response(
                {'error': '文章不存在或无权限'},
                status=status.HTTP_404_NOT_FOUND
            )

class PostPermanentDeleteView(views.APIView):
    """彻底删除文章视图"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='彻底删除文章',
        operation_description='从回收站中永久删除文章，此操作不可恢复。',
        responses={
            204: '删除成功',
            404: '文章不存在或无权限'
        }
    )
    def delete(self, request, pk):
        try:
            post = Post.objects.get(
                Q(author=request.user) | Q(author__is_staff=True),
                pk=pk,
                is_deleted=True
            )
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response(
                {'error': '文章不存在或无权限'},
                status=status.HTTP_404_NOT_FOUND
            )

class PostEmptyTrashView(views.APIView):
    """清空回收站视图"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary='清空回收站',
        operation_description='清空回收站中的所有文章，此操作不可恢复。管理员可以清空所有文章，普通用户只能清空自己的文章。',
        responses={
            204: '清空成功',
        }
    )
    def delete(self, request):
        if request.user.is_staff:
            Post.objects.filter(is_deleted=True).delete()
        else:
            Post.objects.filter(is_deleted=True, author=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 