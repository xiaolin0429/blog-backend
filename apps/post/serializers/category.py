from rest_framework import serializers

from apps.core.serializers import TimezoneSerializerMixin

from ..models import Category


class CategorySerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """分类序列化器"""

    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    level = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "parent",
            "parent_name",
            "children",
            "level",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_children(self, obj):
        """获取子分类"""
        children = obj.children.all().order_by("order", "id")
        return CategorySerializer(children, many=True, context=self.context).data

    def get_level(self, obj):
        """获取分类层级"""
        level = 0
        parent = obj.parent
        while parent:
            level += 1
            parent = parent.parent
        return level
