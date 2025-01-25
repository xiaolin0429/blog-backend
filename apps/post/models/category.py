from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """文章分类"""

    name = models.CharField(_("名称"), max_length=50, unique=True)
    description = models.TextField(_("描述"), blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("父分类"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    order = models.IntegerField(_("排序"), default=0)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)

    class Meta:
        app_label = "post"
        verbose_name = _("分类")
        verbose_name_plural = _("分类")
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def can_delete(self):
        """检查分类是否可以删除

        Returns:
            bool: 如果分类链路上没有文章引用，则返回True
        """
        from apps.post.models import Post

        # 检查当前分类是否有文章引用
        has_posts = Post.objects.filter(category=self).exists()
        if has_posts:
            return False

        # 递归检查子分类
        for child in self.children.all():
            if not child.can_delete():
                return False

        return True

    def delete(self, *args, **kwargs):
        """重写删除方法，添加删除前检查"""
        if not self.can_delete():
            raise ValidationError("该分类或其子分类下存在文章，无法删除")
        # 递归删除子分类
        for child in self.children.all():
            child.delete()
        super().delete(*args, **kwargs)
