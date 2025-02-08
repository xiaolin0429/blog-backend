from django.db.models import Count, Q
from django.utils.html import mark_safe

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.response import error_response, success_response

from ..models import Category, Post, Tag
from ..serializers import PostListSerializer


class SearchSuggestView(APIView):
    """搜索建议视图"""

    @swagger_auto_schema(
        operation_summary="获取搜索建议",
        operation_description="根据输入的关键词返回搜索建议",
        manual_parameters=[
            openapi.Parameter(
                "keyword",
                openapi.IN_QUERY,
                description="搜索关键词",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="返回结果数量限制",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=10,
            ),
        ],
        responses={
            200: openapi.Response(
                description="搜索建议列表",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "suggestions": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "type": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "title": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "excerpt": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "category": openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "id": openapi.Schema(
                                                        type=openapi.TYPE_INTEGER
                                                    ),
                                                    "name": openapi.Schema(
                                                        type=openapi.TYPE_STRING
                                                    ),
                                                    "level": openapi.Schema(
                                                        type=openapi.TYPE_INTEGER
                                                    ),
                                                },
                                            ),
                                            "post_count": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "level": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                        },
                                    ),
                                )
                            },
                        ),
                    },
                ),
            )
        },
    )
    def get(self, request):
        try:
            keyword = request.query_params.get("keyword")
            if not keyword:
                return error_response(code=400, message="搜索关键词不能为空")

            limit = int(request.query_params.get("limit", 10))
            suggestions = []

            # 搜索文章标题
            posts = Post.objects.filter(
                Q(title__icontains=keyword) | Q(excerpt__icontains=keyword),
                is_deleted=False,
                status="published",
            ).select_related("category")[:limit]

            for post in posts:
                suggestions.append(
                    {
                        "type": "post",
                        "id": post.id,
                        "title": post.title,
                        "excerpt": post.excerpt[:100] if post.excerpt else "",
                        "category": {
                            "id": post.category.id,
                            "name": post.category.name,
                            "level": post.category.level,
                        }
                        if post.category
                        else None,
                        "post_count": None,  # 文章类型不需要post_count
                        "level": None,  # 文章类型不需要level
                    }
                )

            # 搜索分类
            categories = Category.objects.filter(name__icontains=keyword).annotate(
                post_count=Count(
                    "post", filter=Q(post__is_deleted=False, post__status="published")
                )
            )[:limit]

            for category in categories:
                suggestions.append(
                    {
                        "type": "category",
                        "id": category.id,
                        "title": category.name,  # 使用title字段保持一致性
                        "excerpt": category.description[:100]
                        if category.description
                        else "",
                        "category": None,  # 分类类型不需要category
                        "post_count": category.post_count,
                        "level": category.level,
                    }
                )

            # 搜索标签
            tags = Tag.objects.filter(name__icontains=keyword).annotate(
                post_count=Count(
                    "post", filter=Q(post__is_deleted=False, post__status="published")
                )
            )[:limit]

            for tag in tags:
                suggestions.append(
                    {
                        "type": "tag",
                        "id": tag.id,
                        "title": tag.name,  # 使用title字段保持一致性
                        "excerpt": tag.description[:100] if tag.description else "",
                        "category": None,  # 标签类型不需要category
                        "post_count": tag.post_count,
                        "level": None,  # 标签类型不需要level
                    }
                )

            # 按相关度排序并限制返回数量
            suggestions = sorted(
                suggestions,
                key=lambda x: (
                    not x["title"].startswith(keyword),  # 优先完全匹配
                    len(x["title"]),  # 其次按标题长度排序
                ),
            )[:limit]

            return success_response(data={"suggestions": suggestions})

        except Exception as e:
            return Response(
                {"code": 500, "message": "搜索失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SearchView(generics.ListAPIView):
    """高级搜索视图"""

    serializer_class = PostListSerializer

    @swagger_auto_schema(
        operation_summary="高级搜索",
        operation_description="支持多字段组合搜索，结果高亮显示",
        manual_parameters=[
            openapi.Parameter(
                "keyword",
                openapi.IN_QUERY,
                description="搜索关键词",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "fields",
                openapi.IN_QUERY,
                description="搜索字段，多个字段用逗号分隔（title,content,excerpt）",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="分类ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "tags",
                openapi.IN_QUERY,
                description="标签ID列表，多个标签用逗号分隔",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "author",
                openapi.IN_QUERY,
                description="作者ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "date_start",
                openapi.IN_QUERY,
                description="开始日期（YYYY-MM-DD）",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "date_end",
                openapi.IN_QUERY,
                description="结束日期（YYYY-MM-DD）",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "highlight",
                openapi.IN_QUERY,
                description="是否高亮显示搜索结果（true/false）",
                type=openapi.TYPE_BOOLEAN,
                required=False,
                default=True,
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="页码，默认1",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "size",
                openapi.IN_QUERY,
                description="每页数量，默认10",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="搜索结果",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "next": openapi.Schema(type=openapi.TYPE_STRING),
                                "previous": openapi.Schema(type=openapi.TYPE_STRING),
                                "results": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "title": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "excerpt": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "content": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "author": openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "id": openapi.Schema(
                                                        type=openapi.TYPE_INTEGER
                                                    ),
                                                    "username": openapi.Schema(
                                                        type=openapi.TYPE_STRING
                                                    ),
                                                    "nickname": openapi.Schema(
                                                        type=openapi.TYPE_STRING
                                                    ),
                                                },
                                            ),
                                            "category": openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "id": openapi.Schema(
                                                        type=openapi.TYPE_INTEGER
                                                    ),
                                                    "name": openapi.Schema(
                                                        type=openapi.TYPE_STRING
                                                    ),
                                                    "level": openapi.Schema(
                                                        type=openapi.TYPE_INTEGER
                                                    ),
                                                },
                                            ),
                                            "tags": openapi.Schema(
                                                type=openapi.TYPE_ARRAY,
                                                items=openapi.Schema(
                                                    type=openapi.TYPE_OBJECT,
                                                    properties={
                                                        "id": openapi.Schema(
                                                            type=openapi.TYPE_INTEGER
                                                        ),
                                                        "name": openapi.Schema(
                                                            type=openapi.TYPE_STRING
                                                        ),
                                                    },
                                                ),
                                            ),
                                            "created_at": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "updated_at": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                        },
                                    ),
                                ),
                            },
                        ),
                        "timestamp": openapi.Schema(type=openapi.TYPE_STRING),
                        "requestId": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "搜索关键词不能为空",
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            # 获取搜索参数
            keyword = request.query_params.get("keyword")
            if not keyword:
                return error_response(code=400, message="搜索关键词不能为空")

            # 构建查询条件
            query = Q()

            # 搜索字段
            fields = request.query_params.get("fields", "title,content,excerpt").split(
                ","
            )
            valid_fields = {"title", "content", "excerpt"}
            search_fields = [f for f in fields if f in valid_fields]

            for field in search_fields:
                query |= Q(**{f"{field}__icontains": keyword})

            # 基础过滤
            queryset = Post.objects.filter(query, is_deleted=False, status="published")

            # 分类过滤
            category = request.query_params.get("category")
            if category:
                queryset = queryset.filter(category_id=category)

            # 标签过滤
            tags = request.query_params.get("tags")
            if tags:
                tag_ids = [int(tid) for tid in tags.split(",") if tid.isdigit()]
                if tag_ids:
                    queryset = queryset.filter(tags__id__in=tag_ids).distinct()

            # 作者过滤
            author = request.query_params.get("author")
            if author:
                queryset = queryset.filter(author_id=author)

            # 日期过滤
            date_start = request.query_params.get("date_start")
            if date_start:
                queryset = queryset.filter(created_at__date__gte=date_start)

            date_end = request.query_params.get("date_end")
            if date_end:
                queryset = queryset.filter(created_at__date__lte=date_end)

            # 分页
            page_size = int(request.query_params.get("size", 10))
            self.pagination_class.page_size = page_size

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = serializer.data

                # 高亮处理
                if request.query_params.get("highlight", "true").lower() == "true":
                    for item in data:
                        for field in search_fields:
                            if field in item and isinstance(item[field], str):
                                item[field] = self._highlight_text(item[field], keyword)

                return success_response(
                    data=self.paginator.get_paginated_response(data).data
                )

            serializer = self.get_serializer(queryset, many=True)
            return success_response(
                data={"results": serializer.data, "count": queryset.count()}
            )

        except Exception as e:
            return Response(
                {"code": 500, "message": "搜索失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _highlight_text(self, text: str, keyword: str) -> str:
        """高亮关键词"""
        if not text or not keyword:
            return text

        # 使用mark_safe确保HTML标签不被转义
        highlighted = text.replace(
            keyword, f'<span class="search-highlight">{keyword}</span>'
        )
        return mark_safe(highlighted)

    def get_queryset(self):
        """默认查询集"""
        return Post.objects.filter(is_deleted=False, status="published")
