from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.core.response import success_response, created_response, error_response
from apps.core.permissions import IsAdminUserOrReadOnly
from ..models import Comment, Post
from ..serializers.comment import CommentSerializer
from ..filters import CommentFilter

class GlobalCommentListView(generics.ListAPIView):
    """全局评论列表视图"""
    serializer_class = CommentSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = CommentFilter
    search_fields = ['content', 'author__username']
    ordering_fields = ['created_at', 'reply_count']
    ordering = ['-created_at']

    def get_queryset(self):
        """获取评论查询集"""
        return Comment.objects.annotate(
            reply_count=Count('replies')
        ).select_related(
            'author', 'post'
        ).prefetch_related(
            'replies', 'replies__author'
        )

    @swagger_auto_schema(
        operation_summary='获取全局评论列表',
        operation_description='获取所有评论列表，支持分页、排序和筛选',
        manual_parameters=[
            openapi.Parameter(
                'page', openapi.IN_QUERY,
                description='页码',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'size', openapi.IN_QUERY,
                description='每页数量',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY,
                description='排序字段，支持created_at和reply_count，前缀-表示降序',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'keyword', openapi.IN_QUERY,
                description='关键词搜索，搜索评论内容和作者用户名',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'post', openapi.IN_QUERY,
                description='按文章ID筛选',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'author', openapi.IN_QUERY,
                description='按作者ID筛选',
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'start_date', openapi.IN_QUERY,
                description='开始日期，格式：YYYY-MM-DD',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'end_date', openapi.IN_QUERY,
                description='结束日期，格式：YYYY-MM-DD',
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: CommentSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """获取评论列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return success_response(data=response.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)

class CommentListCreateView(generics.ListCreateAPIView):
    """评论列表和创建视图"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """获取评论列表，只返回顶级评论"""
        return Comment.objects.filter(
            post_id=self.kwargs.get('post_id'),
            parent=None
        ).annotate(
            reply_count=Count('replies')
        ).select_related('author').prefetch_related('replies', 'replies__author')

    @swagger_auto_schema(
        operation_summary='获取文章评论列表',
        operation_description='获取指定文章的评论列表，包含评论的回复',
        manual_parameters=[
            openapi.Parameter(
                'post_id', openapi.IN_PATH,
                description='文章ID',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: CommentSerializer(many=True),
            404: '文章不存在'
        }
    )
    def get(self, request, *args, **kwargs):
        """获取评论列表"""
        post_id = self.kwargs.get('post_id')
        if not Post.objects.filter(id=post_id).exists():
            return error_response(
                code=404,
                message="文章不存在",
                status_code=status.HTTP_404_NOT_FOUND
            )
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_summary='创建评论',
        operation_description='为指定文章创建新评论',
        manual_parameters=[
            openapi.Parameter(
                'post_id', openapi.IN_PATH,
                description='文章ID',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='评论内容'),
                'parent': openapi.Schema(type=openapi.TYPE_INTEGER, description='父评论ID，可选'),
            }
        ),
        responses={
            201: CommentSerializer,
            400: '参数错误',
            404: '文章不存在'
        }
    )
    def post(self, request, *args, **kwargs):
        """创建评论"""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        
        serializer = self.get_serializer(data={
            'post': post.id,
            'content': request.data.get('content'),
            'parent': request.data.get('parent')
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return created_response(data=serializer.data)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """评论详情、更新和删除视图"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """获取评论查询集"""
        return Comment.objects.annotate(
            reply_count=Count('replies')
        ).select_related('author').prefetch_related('replies', 'replies__author')

    @swagger_auto_schema(
        operation_summary='获取评论详情',
        operation_description='获取指定评论的详细信息',
        responses={
            200: CommentSerializer,
            404: '评论不存在'
        }
    )
    def get(self, request, *args, **kwargs):
        """获取评论详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_summary='更新评论',
        operation_description='更新指定评论的内容',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='评论内容'),
            }
        ),
        responses={
            200: CommentSerializer,
            400: '参数错误',
            403: '无权限修改',
            404: '评论不存在'
        }
    )
    def put(self, request, *args, **kwargs):
        """更新评论"""
        instance = self.get_object()
        if instance.author != request.user:
            return error_response(
                code=403,
                message="无权限修改此评论",
                status_code=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(data=serializer.data)

    @swagger_auto_schema(
        operation_summary='删除评论',
        operation_description='删除指定评论',
        responses={
            204: '删除成功',
            403: '无权限删除',
            404: '评论不存在'
        }
    )
    def delete(self, request, *args, **kwargs):
        """删除评论"""
        instance = self.get_object()
        if instance.author != request.user:
            return error_response(
                code=403,
                message="无权限删除此评论",
                status_code=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT) 