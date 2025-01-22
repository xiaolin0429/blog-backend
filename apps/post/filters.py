from django_filters import rest_framework as filters
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import logging
from .models import Comment

logger = logging.getLogger(__name__)

class CommentFilter(filters.FilterSet):
    """评论过滤器"""
    keyword = filters.CharFilter(method='filter_keyword')
    start_date = filters.DateFilter(field_name='created_at', method='filter_start_date')
    end_date = filters.DateFilter(field_name='created_at', method='filter_end_date')
    
    class Meta:
        model = Comment
        fields = {
            'post': ['exact'],
            'author': ['exact'],
            'parent': ['exact', 'isnull'],
        }
    
    def filter_keyword(self, queryset, name, value):
        """关键词搜索，支持评论内容和作者用户名"""
        if value:
            return queryset.filter(
                Q(content__icontains=value) |
                Q(author__username__icontains=value)
            )
        return queryset

    def filter_start_date(self, queryset, name, value):
        """过滤开始日期"""
        if value:
            try:
                # 将日期转换为datetime，设置时间为当天的开始（00:00:00）
                start_datetime = timezone.make_aware(
                    datetime.combine(value, datetime.min.time())
                )
                logger.debug(f"Filtering comments after {start_datetime}")
                queryset = queryset.filter(created_at__gte=start_datetime)
                logger.debug(f"Found {queryset.count()} comments after {start_datetime}")
                return queryset
            except Exception as e:
                logger.error(f"Error filtering start date: {e}")
        return queryset

    def filter_end_date(self, queryset, name, value):
        """过滤结束日期"""
        if value:
            try:
                # 将日期转换为datetime，设置时间为当天的结束（23:59:59.999999）
                end_datetime = timezone.make_aware(
                    datetime.combine(value, datetime.max.time())
                )
                logger.debug(f"Filtering comments before {end_datetime}")
                queryset = queryset.filter(created_at__lte=end_datetime)
                logger.debug(f"Found {queryset.count()} comments before {end_datetime}")
                return queryset
            except Exception as e:
                logger.error(f"Error filtering end date: {e}")
        return queryset 