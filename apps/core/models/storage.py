from django.db import models
from django.utils import timezone


class FileStorage(models.Model):
    """文件存储模型"""

    file_id = models.CharField(max_length=32, primary_key=True, help_text="文件ID")
    original_name = models.CharField(max_length=255, help_text="原始文件名")
    file_type = models.CharField(max_length=20, help_text="文件类型")
    mime_type = models.CharField(max_length=100, help_text="MIME类型")
    file_size = models.BigIntegerField(help_text="文件大小(字节)")
    file_content = models.BinaryField(help_text="文件内容")
    created_at = models.DateTimeField(default=timezone.now, help_text="创建时间")
    updated_at = models.DateTimeField(auto_now=True, help_text="更新时间")

    class Meta:
        db_table = "core_file_storage"
        ordering = ["-created_at"]
        verbose_name = "文件存储"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.original_name} ({self.file_type})"
