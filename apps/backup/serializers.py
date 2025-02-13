from rest_framework import serializers

from .models import Backup, BackupConfig


class BackupSerializer(serializers.ModelSerializer):
    backup_type_display = serializers.CharField(
        source="get_backup_type_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Backup
        fields = [
            "id",
            "name",
            "backup_type",
            "backup_type_display",
            "description",
            "file_path",
            "file_size",
            "status",
            "status_display",
            "error_message",
            "is_auto",
            "created_at",
            "started_at",
            "completed_at",
            "created_by",
            "created_by_name",
        ]
        read_only_fields = [
            "file_path",
            "file_size",
            "status",
            "error_message",
            "is_auto",
            "created_at",
            "started_at",
            "completed_at",
            "created_by",
        ]


class BackupConfigSerializer(serializers.ModelSerializer):
    backup_type_display = serializers.CharField(
        source="get_backup_type_display", read_only=True
    )
    frequency_display = serializers.CharField(
        source="get_frequency_display", read_only=True
    )

    class Meta:
        model = BackupConfig
        fields = [
            "id",
            "enabled",
            "backup_type",
            "backup_type_display",
            "frequency",
            "frequency_display",
            "retention_days",
            "backup_time",
            "last_backup",
            "next_backup",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["last_backup", "next_backup", "created_at", "updated_at"]
