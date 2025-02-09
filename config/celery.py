import os

from django.conf import settings

from celery import Celery
from celery.schedules import crontab

# 设置默认的 Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("blog")

# 使用 Django 的配置文件配置 Celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# 自动发现任务
app.autodiscover_tasks()

# 配置定时任务
app.conf.beat_schedule = {
    "update-user-statistics": {
        "task": "apps.core.tasks.update_user_statistics",
        "schedule": crontab(minute=0, hour=0),  # 每天凌晨执行
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
