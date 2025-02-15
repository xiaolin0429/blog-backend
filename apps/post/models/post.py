from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    """文章"""

    STATUS_CHOICES = (
        ("draft", _("草稿")),
        ("published", _("已发布")),
        ("archived", _("已归档")),
    )

    title = models.CharField(_("标题"), max_length=200)
    content = models.TextField(_("内容"))
    excerpt = models.TextField(_("摘要"), blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("作者"), on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        "Category",
        verbose_name=_("分类"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField("Tag", verbose_name=_("标签"), blank=True)
    status = models.CharField(
        _("状态"), max_length=10, choices=STATUS_CHOICES, default="draft"
    )
    cover = models.CharField(_("封面图"), max_length=500, blank=True, null=True)
    pinned = models.BooleanField(_("是否置顶"), default=False)
    allow_comment = models.BooleanField(_("允许评论"), default=True)
    views = models.PositiveIntegerField(_("浏览量"), default=0)
    likes = models.PositiveIntegerField(_("点赞数"), default=0)
    created_at = models.DateTimeField(_("创建时间"), default=timezone.now)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)
    published_at = models.DateTimeField(_("发布时间"), null=True, blank=True)
    deleted_at = models.DateTimeField(_("删除时间"), null=True, blank=True)
    is_deleted = models.BooleanField(_("是否删除"), default=False)

    # 新增自动保存相关字段
    auto_save_content = models.JSONField(null=True, blank=True, help_text="自动保存的内容")
    auto_save_title = models.CharField(
        _("自动保存标题"), max_length=200, blank=True, null=True
    )
    auto_save_excerpt = models.TextField(_("自动保存摘要"), blank=True, null=True)
    auto_save_time = models.DateTimeField(_("自动保存时间"), null=True, blank=True)
    version = models.IntegerField(default=1, help_text="文章版本号")

    class Meta:
        app_label = "post"
        verbose_name = _("文章")
        verbose_name_plural = _("文章")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """重写保存方法，处理发布时间"""
        if self.status == "published" and not self.published_at:
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
        self.status = "draft"  # 恢复时默认设为草稿状态
        self.save()
