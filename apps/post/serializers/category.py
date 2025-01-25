from rest_framework import serializers

from apps.core.serializers import TimezoneSerializerMixin

from ..models import Category


class CategorySerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """分类序列化器"""

    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "parent",
            "parent_name",
            "children",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_children(self, obj):
        """获取子分类"""
        children = obj.children.all()
        return CategorySerializer(children, many=True, context=self.context).data
