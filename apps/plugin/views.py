from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.response import success_response, error_response
from apps.core.permissions import IsAdminUserOrReadOnly
from . import models, serializers

# Create your views here.

class PluginListView(generics.ListAPIView):
    """插件列表视图"""
    queryset = models.Plugin.objects.all()
    serializer_class = serializers.PluginSerializer
    permission_classes = [permissions.IsAdminUser]

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return error_response(code=403, message="权限不足")
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)

class PluginInstallView(generics.CreateAPIView):
    """插件安装视图"""
    serializer_class = serializers.PluginInstallSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return error_response(code=403, message="权限不足")
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return success_response(data=serializer.data)
        except Exception as e:
            error_data = None
            if hasattr(e, 'detail'):
                error_data = {"errors": e.detail}
            return error_response(
                code=400,
                message="安装插件失败",
                data=error_data
            )

    def perform_create(self, serializer):
        # 实现插件安装逻辑
        serializer.save(enabled=False, config={})

class PluginUninstallView(generics.DestroyAPIView):
    """插件卸载视图"""
    queryset = models.Plugin.objects.all()
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'name'
    lookup_url_kwarg = 'plugin_id'

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return error_response(code=403, message="权限不足")
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return success_response(message="插件已卸载")
        except models.Plugin.DoesNotExist:
            return error_response(
                code=404,
                message="插件不存在"
            )

class PluginEnableView(APIView):
    """插件启用视图"""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, plugin_id):
        if not request.user.is_staff:
            return error_response(code=403, message="权限不足")
        try:
            plugin = models.Plugin.objects.get(name=plugin_id)
            plugin.enabled = True
            plugin.save()
            return success_response(message="插件已启用")
        except models.Plugin.DoesNotExist:
            return error_response(
                code=404,
                message="插件不存在"
            )

class PluginDisableView(APIView):
    """插件禁用视图"""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, plugin_id):
        if not request.user.is_staff:
            return error_response(code=403, message="权限不足")
        try:
            plugin = models.Plugin.objects.get(name=plugin_id)
            plugin.enabled = False
            plugin.save()
            return success_response(message="插件已禁用")
        except models.Plugin.DoesNotExist:
            return error_response(
                code=404,
                message="插件不存在"
            )

class PluginSettingsView(generics.RetrieveUpdateAPIView):
    """插件配置视图"""
    queryset = models.Plugin.objects.all()
    serializer_class = serializers.PluginConfigSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'name'
    lookup_url_kwarg = 'plugin_id'

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return error_response(code=403, message="权限不足")
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return success_response(data=serializer.data)
        except models.Plugin.DoesNotExist:
            return error_response(
                code=404,
                message="插件不存在"
            )

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return error_response(code=403, message="权限不足")
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return success_response(data=serializer.data)
        except models.Plugin.DoesNotExist:
            return error_response(
                code=404,
                message="插件不存在"
            )
        except Exception as e:
            error_data = None
            if hasattr(e, 'detail'):
                error_data = {"errors": e.detail}
            return error_response(
                code=400,
                message="更新配置失败",
                data=error_data
            )
