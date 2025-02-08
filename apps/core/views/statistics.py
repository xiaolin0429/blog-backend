from datetime import datetime, timedelta

from django.core.cache import cache
from django.db.models import Count, Q, Sum
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models.statistics import UserStatistics, VisitStatistics
from apps.post.models import Category, Post, Tag
from apps.post.models.comment import Comment


class BaseStatisticsView(APIView):
    """统计视图基类，遵循依赖倒转原则"""

    permission_classes = [IsAuthenticated]
    cache_timeout = 3600  # 缓存1小时

    def get_date_range(self, request):
        """获取日期范围"""
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            # 默认查询最近7天
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
        return start_date, end_date

    def get_cache_key(self, prefix, start_date, end_date):
        """生成缓存key"""
        return f"{prefix}_{start_date}_{end_date}"


class ContentStatisticsView(BaseStatisticsView):
    """内容统计视图"""

    def get(self, request):
        try:
            start_date, end_date = self.get_date_range(request)
            cache_key = self.get_cache_key("content_stats", start_date, end_date)

            # 尝试从缓存获取数据
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)

            # 文章统计
            posts_data = self._get_posts_statistics(start_date, end_date)

            # 评论统计
            comments_data = self._get_comments_statistics(start_date, end_date)

            # 分类统计
            categories_data = self._get_categories_statistics()

            # 标签统计
            tags_data = self._get_tags_statistics()

            # 组装数据
            data = {
                "posts": posts_data,
                "comments": comments_data,
                "categories": categories_data,
                "tags": tags_data,
            }

            # 缓存数据
            cache.set(cache_key, data, self.cache_timeout)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def _get_posts_statistics(self, start_date, end_date):
        """获取文章统计数据"""
        try:
            # 基础查询集
            posts = Post.objects.filter(
                created_at__date__range=[start_date, end_date], is_deleted=False
            )

            # 按状态统计
            total = posts.count()

            # 检查status字段是否存在
            if hasattr(Post, "status"):
                published = posts.filter(status="published").count()
                draft = posts.filter(status="draft").count()
                private = posts.filter(status="private").count()
            else:
                published = total
                draft = 0
                private = 0

            # 热门作者
            top_authors = (
                Post.objects.filter(is_deleted=False)
                .values("author_id", "author__username")
                .annotate(
                    post_count=Count("id"),
                )
                .order_by("-post_count")[:10]
            )

            return {
                "total": total,
                "published": published,
                "draft": draft,
                "private": private,
                "topAuthors": [
                    {
                        "id": author["author_id"],
                        "username": author["author__username"],
                        "postCount": author["post_count"],
                    }
                    for author in top_authors
                ],
            }
        except Exception as e:
            return {
                "total": 0,
                "published": 0,
                "draft": 0,
                "private": 0,
                "topAuthors": [],
            }

    def _get_comments_statistics(self, start_date, end_date):
        """获取评论统计数据"""
        try:
            # 基础查询集
            comments = Comment.objects.filter(
                created_at__date__range=[start_date, end_date]
            )

            # 按状态统计
            total = comments.count()
            approved = comments.filter(status="approved").count()
            pending = comments.filter(status="pending").count()
            spam = comments.filter(status="spam").count()

            return {
                "total": total,
                "approved": approved,
                "pending": pending,
                "spam": spam,
            }
        except Exception as e:
            return {"total": 0, "approved": 0, "pending": 0, "spam": 0}

    def _get_categories_statistics(self):
        """获取分类统计数据"""
        try:
            # 总数统计
            total = Category.objects.count()

            # 热门分类（按文章数）
            top_categories = (
                Category.objects.annotate(
                    post_count=Count(
                        "post",
                        filter=Q(post__status="published", post__is_deleted=False),
                    )
                )
                .filter(post_count__gt=0)
                .order_by("-post_count")[:10]
            )

            return {
                "total": total,
                "topCategories": [
                    {
                        "id": category.id,
                        "name": category.name,
                        "postCount": category.post_count,
                    }
                    for category in top_categories
                ],
            }
        except Exception as e:
            return {"total": 0, "topCategories": []}

    def _get_tags_statistics(self):
        """获取标签统计数据"""
        try:
            # 总数统计
            total = Tag.objects.count()

            # 热门标签（按文章数）
            top_tags = (
                Tag.objects.annotate(
                    post_count=Count(
                        "post",
                        filter=Q(post__status="published", post__is_deleted=False),
                    )
                )
                .filter(post_count__gt=0)
                .order_by("-post_count")[:10]
            )

            return {
                "total": total,
                "topTags": [
                    {
                        "id": tag.id,
                        "name": tag.name,
                        "postCount": tag.post_count,
                    }
                    for tag in top_tags
                ],
            }
        except Exception as e:
            return {"total": 0, "topTags": []}


class VisitStatisticsView(BaseStatisticsView):
    """访问统计视图"""

    def get(self, request):
        start_date, end_date = self.get_date_range(request)
        cache_key = self.get_cache_key("visit_stats", start_date, end_date)

        # 尝试从缓存获取数据
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # 查询统计数据
        stats = VisitStatistics.objects.filter(
            date__range=[start_date, end_date]
        ).order_by("date")

        # 准备返回数据
        data = {
            "total": {
                "pv": sum(s.pv for s in stats),
                "uv": sum(s.uv for s in stats),
                "ip": sum(s.ip_count for s in stats),
            },
            "trends": [
                {
                    "date": s.date.strftime("%Y-%m-%d"),
                    "pv": s.pv,
                    "uv": s.uv,
                    "ip": s.ip_count,
                }
                for s in stats
            ],
        }

        # 缓存数据
        cache.set(cache_key, data, self.cache_timeout)
        return Response(data)


class UserStatisticsView(BaseStatisticsView):
    """用户统计视图"""

    def get(self, request):
        try:
            start_date, end_date = self.get_date_range(request)
            cache_key = self.get_cache_key("user_stats", start_date, end_date)

            # 尝试从缓存获取数据
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)

            # 查询统计数据
            stats = UserStatistics.objects.filter(
                date__range=[start_date, end_date]
            ).order_by("date")

            # 准备返回数据
            last_stat = stats.last()
            data = {
                "total": {
                    "total_users": last_stat.total_users if last_stat else 0,
                    "active_users": sum(s.active_users for s in stats) if stats else 0,
                    "new_users": sum(s.new_users for s in stats) if stats else 0,
                },
                "trends": [
                    {
                        "date": s.date.strftime("%Y-%m-%d"),
                        "total_users": s.total_users,
                        "active_users": s.active_users,
                        "new_users": s.new_users,
                    }
                    for s in stats
                ],
            }

            # 缓存数据
            cache.set(cache_key, data, self.cache_timeout)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
