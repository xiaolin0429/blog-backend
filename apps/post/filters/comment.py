from datetime import datetime, time

import django_filters
from django.db.models import Q
from django.utils import timezone

from ..models import Comment


class CommentFilter(django_filters.FilterSet):
    """评论过滤器"""

    keyword = django_filters.CharFilter(method="filter_keyword")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", method="filter_start_date"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", method="filter_end_date"
    )
    post = django_filters.NumberFilter(field_name="post")
    author = django_filters.NumberFilter(field_name="author")

    class Meta:
        model = Comment
        fields = ["keyword", "start_date", "end_date", "post", "author"]

    def filter_keyword(self, queryset, name, value):
        """关键词过滤"""
        if not value:
            return queryset
        return queryset.filter(
            Q(content__icontains=value) | Q(author__username__icontains=value)
        )

    def filter_start_date(self, queryset, name, value):
        """开始日期过滤"""
        if not value:
            return queryset
        # 将日期转换为日期时间,设置时间为当天的开始(00:00:00)
        start_datetime = datetime.combine(value, time.min)
        start_datetime = timezone.make_aware(start_datetime)
        print(f"Filtering comments after {start_datetime}")
        filtered_queryset = queryset.filter(created_at__gte=start_datetime)
        print(f"Found {filtered_queryset.count()} comments after {start_datetime}")
        return filtered_queryset

    def filter_end_date(self, queryset, name, value):
        """结束日期过滤"""
        if not value:
            return queryset
        # 将日期转换为日期时间,设置时间为当天的结束(23:59:59.999999)
        end_datetime = datetime.combine(value, time.max)
        end_datetime = timezone.make_aware(end_datetime)
        return queryset.filter(created_at__lte=end_datetime)
