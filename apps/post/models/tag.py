from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """文章标签"""

    name = models.CharField(_("名称"), max_length=50, unique=True)
    description = models.TextField(_("描述"), blank=True, null=True)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)

    class Meta:
        app_label = "post"
        verbose_name = _("标签")
        verbose_name_plural = _("标签")
        ordering = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_count = None

    def __str__(self):
        return self.name
