from django.db import models
from django.utils import timezone


def get_today():
    return timezone.now().date()


class BaseStatistics(models.Model):
    """统计基类，遵循开闭原则和接口隔离原则"""

    date = models.DateField(default=get_today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = "core"


class VisitStatistics(BaseStatistics):
    """访问量统计"""

    pv = models.IntegerField(default=0, help_text="页面浏览量")
    uv = models.IntegerField(default=0, help_text="独立访客数")
    ip_count = models.IntegerField(default=0, help_text="IP数")

    class Meta:
        app_label = "core"
        db_table = "core_visit_statistics"
        ordering = ["-date"]
        verbose_name = "访问统计"
        verbose_name_plural = verbose_name


class UserStatistics(BaseStatistics):
    """用户统计"""

    total_users = models.IntegerField(default=0, help_text="总用户数")
    active_users = models.IntegerField(default=0, help_text="活跃用户数")
    new_users = models.IntegerField(default=0, help_text="新增用户数")

    class Meta:
        app_label = "core"
        db_table = "core_user_statistics"
        ordering = ["-date"]
        verbose_name = "用户统计"
        verbose_name_plural = verbose_name
