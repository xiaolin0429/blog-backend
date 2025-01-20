from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """文章分类"""
    name = models.CharField(_('名称'), max_length=50, unique=True)
    description = models.TextField(_('描述'), blank=True, null=True)
    parent = models.ForeignKey('self', verbose_name=_('父分类'), on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.IntegerField(_('排序'), default=0)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        app_label = 'post'
        verbose_name = _('分类')
        verbose_name_plural = _('分类')
        ordering = ['order', 'id']

    def __str__(self):
        return self.name 