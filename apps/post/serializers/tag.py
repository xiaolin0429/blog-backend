from rest_framework import serializers
from apps.core.serializers import TimezoneSerializerMixin
from ..models import Tag

class TagSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """标签序列化器"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['created_at'] 