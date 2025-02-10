from django.http import FileResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Backup, BackupConfig
from .serializers import BackupConfigSerializer, BackupSerializer
from .services import BackupService


class BackupViewSet(viewsets.ModelViewSet):
    """
    备份管理视图集

    提供备份的CRUD操作，仅管理员可访问
    """

    queryset = Backup.objects.all()
    serializer_class = BackupSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["backup_type", "status", "is_auto"]
    ordering_fields = ["created_at", "started_at", "completed_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        backup = serializer.save(created_by=self.request.user)
        backup.file_size = backup.file_path.size if backup.file_path else 0
        backup.save()

    @action(detail=False, methods=["post"])
    def create_full_backup(self, request):
        """创建完整备份（包括数据库和媒体文件）"""
        try:
            name = request.data.get(
                "name", f"完整备份 {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            description = request.data.get("description", "")
            backup_type = request.data.get("backup_type", "full")

            # 创建数据库备份
            backup = BackupService.create_backup(
                name=name,
                backup_type=backup_type,
                description=description,
                user=request.user,
            )

            # 备份媒体文件
            media_backup_path = BackupService.backup_media_files(backup)

            return Response(
                {
                    "code": 0,
                    "message": _("备份创建成功"),
                    "data": {
                        "backup_id": backup.id,
                        "media_backup_path": media_backup_path,
                    },
                }
            )
        except Exception as e:
            return Response(
                {"code": 1, "message": _("备份创建失败：%s") % str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """从备份文件恢复数据"""
        backup = self.get_object()
        try:
            BackupService.restore_from_backup(backup)
            return Response({"code": 0, "message": _("恢复成功")})
        except Exception as e:
            return Response(
                {"code": 1, "message": _("恢复失败：%s") % str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """下载备份文件"""
        backup = self.get_object()
        if not backup.file_path:
            return Response(
                {"code": 1, "message": _("备份文件不存在")}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            response = FileResponse(backup.file_path.open("rb"))
            response["Content-Type"] = "application/octet-stream"
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{backup.file_path.name}"'
            return response
        except Exception as e:
            return Response(
                {"code": 1, "message": _("下载失败：%s") % str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class BackupConfigViewSet(viewsets.ModelViewSet):
    """备份配置视图集"""

    queryset = BackupConfig.objects.all()
    serializer_class = BackupConfigSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        """测试备份配置"""
        config = self.get_object()
        try:
            name = f"测试备份 {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
            description = f"测试备份配置 ID: {config.id}"

            backup = BackupService.create_backup(
                name=name,
                backup_type=config.backup_type,
                description=description,
                user=request.user,
            )

            if backup.backup_type in ["full", "files"]:
                BackupService.backup_media_files(backup)

            return Response(
                {"code": 0, "message": _("测试备份已启动"), "data": {"backup_id": backup.id}}
            )
        except Exception as e:
            return Response(
                {"code": 1, "message": _("测试备份失败：%s") % str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
