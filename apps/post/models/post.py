from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Post(models.Model):
    """文章"""
    STATUS_CHOICES = (
        ('draft', _('草稿')),
        ('published', _('已发布')),
        ('archived', _('已归档')),
    )

    title = models.CharField(_('标题'), max_length=200)
    content = models.TextField(_('内容'))
    excerpt = models.TextField(_('摘要'), blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('作者'), on_delete=models.CASCADE)
    category = models.ForeignKey('Category', verbose_name=_('分类'), on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField('Tag', verbose_name=_('标签'), blank=True)
    status = models.CharField(_('状态'), max_length=10, choices=STATUS_CHOICES, default='draft')
    views = models.PositiveIntegerField(_('浏览量'), default=0)
    likes = models.PositiveIntegerField(_('点赞数'), default=0)
    created_at = models.DateTimeField(_('创建时间'), default=timezone.now)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    published_at = models.DateTimeField(_('发布时间'), null=True, blank=True)
    deleted_at = models.DateTimeField(_('删除时间'), null=True, blank=True)
    is_deleted = models.BooleanField(_('是否删除'), default=False)

    class Meta:
        app_label = 'post'
        verbose_name = _('文章')
        verbose_name_plural = _('文章')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """重写保存方法，处理发布时间"""
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """恢复删除"""
        self.is_deleted = False
        self.deleted_at = None
        self.status = 'draft'  # 恢复时默认设为草稿状态
        self.save() 