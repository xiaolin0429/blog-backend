from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """自定义用户模型"""

    email = models.EmailField(_("邮箱地址"), unique=True)
    nickname = models.CharField(_("昵称"), max_length=20, blank=True, default="")
    avatar = models.ImageField(_("头像"), upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(_("个人简介"), max_length=500, blank=True, default="")
    storage_quota = models.BigIntegerField(
        _("存储配额"), help_text="用户存储配额(字节)", default=1024 * 1024 * 1024  # 1GB
    )

    class Meta:
        verbose_name = _("用户")
        verbose_name_plural = verbose_name
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username
