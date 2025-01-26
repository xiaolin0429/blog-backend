from rest_framework import serializers

from apps.core.serializers import TimezoneSerializerMixin
from ..models import Tag, Post


class DuplicateTagError(Exception):
    """标签名称重复异常"""

    pass


class TagSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """标签序列化器"""

    post_count = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ["id", "name", "description", "post_count", "created_at", "posts"]
        read_only_fields = ["created_at", "post_count", "posts"]

    def get_post_count(self, obj):
        """获取文章数量"""
        return obj.post_set.count()

    def get_posts(self, obj):
        """获取最近的文章列表（仅在详情接口返回）"""
        if self.context.get('detail'):
            from ..serializers import PostBriefSerializer
            return PostBriefSerializer(
                obj.post_set.order_by('-created_at')[:10], 
                many=True
            ).data
        return None

    def validate_name(self, value):
        """验证标签名称"""
        if not value:
            raise serializers.ValidationError("标签名称不能为空")
        if len(value) < 2 or len(value) > 50:
            raise serializers.ValidationError("标签名称长度必须在2-50个字符之间")
        return value

    def validate(self, attrs):
        """验证整个数据"""
        # 检查标签名称是否已存在
        name = attrs.get("name")
        if name:
            instance = self.instance
            if (
                Tag.objects.filter(name=name)
                .exclude(id=instance.id if instance else None)
                .exists()
            ):
                raise DuplicateTagError("标签名称已存在")
        return attrs
