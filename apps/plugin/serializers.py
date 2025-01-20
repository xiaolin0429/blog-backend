from rest_framework import serializers
from apps.core.serializers import TimezoneSerializerMixin
from . import models

class PluginSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """插件序列化器"""
    class Meta:
        model = models.Plugin
        fields = ['id', 'name', 'description', 'version', 'enabled', 'config',
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class PluginInstallSerializer(TimezoneSerializerMixin, serializers.Serializer):
    """插件安装序列化器"""
    file = serializers.FileField(write_only=True)

    def validate_file(self, value):
        # TODO: 验证插件文件格式和内容
        return value

    def create(self, validated_data):
        # TODO: 实现插件安装逻辑
        pass

class PluginConfigSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """插件配置序列化器"""
    class Meta:
        model = models.Plugin
        fields = ['config'] 