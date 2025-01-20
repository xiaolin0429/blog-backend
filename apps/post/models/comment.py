from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Comment(models.Model):
    """文章评论"""
    post = models.ForeignKey('Post', verbose_name=_('文章'), on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('作者'), on_delete=models.CASCADE)
    content = models.TextField(_('内容'))
    parent = models.ForeignKey('self', verbose_name=_('父评论'), on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        app_label = 'post'
        verbose_name = _('评论')
        verbose_name_plural = _('评论')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username} on {self.post.title}' 