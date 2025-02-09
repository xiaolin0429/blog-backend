from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone

from celery import shared_task

from apps.core.models import UserStatistics

User = get_user_model()


@shared_task
def update_user_statistics():
    """
    更新用户统计数据
    1. 计算总用户数
    2. 计算今日活跃用户数（24小时内有登录记录的用户）
    3. 计算新增用户数（今日注册的用户）
    """
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # 计算总用户数
    total_users = User.objects.filter(is_active=True).count()

    # 计算活跃用户数（24小时内有登录记录的用户）
    active_users = User.objects.filter(last_login__date=today, is_active=True).count()

    # 计算新增用户数
    new_users = User.objects.filter(date_joined__date=today, is_active=True).count()

    # 更新或创建统计记录
    UserStatistics.objects.update_or_create(
        date=today,
        defaults={
            "total_users": total_users,
            "active_users": active_users,
            "new_users": new_users,
        },
    )

    return {
        "date": today.isoformat(),
        "total_users": total_users,
        "active_users": active_users,
        "new_users": new_users,
    }
