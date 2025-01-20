from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from . import models, serializers

# Create your views here.

class PluginListView(generics.ListAPIView):
    """插件列表视图"""
    queryset = models.Plugin.objects.all()
    serializer_class = serializers.PluginSerializer
    permission_classes = [permissions.IsAdminUser]

class PluginInstallView(generics.CreateAPIView):
    """插件安装视图"""
    serializer_class = serializers.PluginInstallSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        # TODO: 实现插件安装逻辑
        pass

class PluginUninstallView(generics.DestroyAPIView):
    """插件卸载视图"""
    queryset = models.Plugin.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'name'
    lookup_url_kwarg = 'plugin_id'

class PluginEnableView(APIView):
    """插件启用视图"""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, plugin_id):
        try:
            plugin = models.Plugin.objects.get(name=plugin_id)
            plugin.enabled = True
            plugin.save()
            return Response({'detail': '插件已启用'})
        except models.Plugin.DoesNotExist:
            return Response(
                {'detail': '插件不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

class PluginDisableView(APIView):
    """插件禁用视图"""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, plugin_id):
        try:
            plugin = models.Plugin.objects.get(name=plugin_id)
            plugin.enabled = False
            plugin.save()
            return Response({'detail': '插件已禁用'})
        except models.Plugin.DoesNotExist:
            return Response(
                {'detail': '插件不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

class PluginSettingsView(generics.RetrieveUpdateAPIView):
    """插件配置视图"""
    queryset = models.Plugin.objects.all()
    serializer_class = serializers.PluginConfigSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'name'
    lookup_url_kwarg = 'plugin_id'
