from django.db import models
from django.utils.translation import gettext_lazy as _

class Plugin(models.Model):
    """插件"""
    name = models.CharField(_('名称'), max_length=100, unique=True)
    description = models.TextField(_('描述'), blank=True)
    version = models.CharField(_('版本'), max_length=50)
    enabled = models.BooleanField(_('是否启用'), default=False)
    config = models.JSONField(_('配置'), default=dict, blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('插件')
        verbose_name_plural = _('插件')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.version})'
