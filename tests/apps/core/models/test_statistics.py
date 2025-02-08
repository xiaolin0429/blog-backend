from datetime import datetime, timedelta

from django.utils import timezone

import pytest

from apps.core.models.statistics import BaseStatistics, UserStatistics, VisitStatistics


@pytest.mark.django_db
class TestVisitStatistics:
    """访问统计测试"""

    def test_create_visit_statistics(self):
        """测试创建访问统计记录"""
        stats = VisitStatistics.objects.create(pv=100, uv=50, ip_count=30)
        assert stats.pv == 100
        assert stats.uv == 50
        assert stats.ip_count == 30
        assert stats.date == timezone.now().date()

    def test_visit_statistics_defaults(self):
        """测试访问统计默认值"""
        stats = VisitStatistics.objects.create()
        assert stats.pv == 0
        assert stats.uv == 0
        assert stats.ip_count == 0

    def test_visit_statistics_ordering(self):
        """测试访问统计排序"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        VisitStatistics.objects.create(date=today)
        VisitStatistics.objects.create(date=yesterday)

        stats = VisitStatistics.objects.all()
        assert stats[0].date == today
        assert stats[1].date == yesterday


@pytest.mark.django_db
class TestUserStatistics:
    """用户统计测试"""

    def test_create_user_statistics(self):
        """测试创建用户统计记录"""
        stats = UserStatistics.objects.create(
            total_users=1000, active_users=500, new_users=50
        )
        assert stats.total_users == 1000
        assert stats.active_users == 500
        assert stats.new_users == 50
        assert stats.date == timezone.now().date()

    def test_user_statistics_defaults(self):
        """测试用户统计默认值"""
        stats = UserStatistics.objects.create()
        assert stats.total_users == 0
        assert stats.active_users == 0
        assert stats.new_users == 0

    def test_user_statistics_ordering(self):
        """测试用户统计排序"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        UserStatistics.objects.create(date=today)
        UserStatistics.objects.create(date=yesterday)

        stats = UserStatistics.objects.all()
        assert stats[0].date == today
        assert stats[1].date == yesterday

    def test_user_statistics_date_range(self):
        """测试用户统计日期范围查询"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        UserStatistics.objects.create(
            date=today, total_users=1000, active_users=500, new_users=50
        )
        UserStatistics.objects.create(
            date=yesterday, total_users=950, active_users=400, new_users=30
        )

        stats = UserStatistics.objects.filter(date__range=[yesterday, today]).order_by(
            "date"
        )

        assert len(stats) == 2
        assert stats[0].date == yesterday
        assert stats[0].total_users == 950
        assert stats[1].date == today
        assert stats[1].total_users == 1000
