from rest_framework import serializers
from apps.core.serializers import TimezoneSerializerMixin
from ..models import Tag

class DuplicateTagError(Exception):
    """标签名称重复异常"""
    pass

class TagSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """标签序列化器"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']

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
        name = attrs.get('name')
        if name:
            instance = self.instance
            if Tag.objects.filter(name=name).exclude(id=instance.id if instance else None).exists():
                raise DuplicateTagError("标签名称已存在")
        return attrs 