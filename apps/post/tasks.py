from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import Post


@shared_task
def cleanup_auto_save_versions():
    """
    清理超过30天的自动保存版本
    """
    # 获取30天前的时间点
    threshold = timezone.now() - timedelta(days=30)

    # 查找所有有自动保存内容的文章
    posts = Post.objects.exclude(auto_save_content__isnull=True)

    cleaned_count = 0
    for post in posts:
        # 检查自动保存时间
        auto_save_time = post.auto_save_content.get("auto_save_time")
        if auto_save_time:
            try:
                save_time = timezone.datetime.fromisoformat(auto_save_time)
                if save_time < threshold:
                    # 清除自动保存内容
                    post.auto_save_content = None
                    post.save(update_fields=["auto_save_content"])
                    cleaned_count += 1
            except (ValueError, TypeError):
                continue

    return f"已清理 {cleaned_count} 篇文章的自动保存内容"
