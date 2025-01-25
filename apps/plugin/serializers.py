from rest_framework import serializers

from apps.core.serializers import TimezoneSerializerMixin

from . import models


class PluginSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """插件序列化器"""

    class Meta:
        model = models.Plugin
        fields = [
            "id",
            "name",
            "description",
            "version",
            "enabled",
            "config",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class PluginInstallSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """插件安装序列化器"""

    class Meta:
        model = models.Plugin
        fields = ["name", "description", "version"]

    def create(self, validated_data):
        return models.Plugin.objects.create(**validated_data)


class PluginConfigSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """插件配置序列化器"""

    config = serializers.DictField(required=True)

    class Meta:
        model = models.Plugin
        fields = ["config"]

    def validate_config(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("配置必须是字典类型")
        return value
