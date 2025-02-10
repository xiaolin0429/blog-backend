from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from apps.backup.services import BackupService


class Command(BaseCommand):
    help = "创建数据库和媒体文件的完整备份"

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str, help="备份名称")
        parser.add_argument("--description", type=str, help="备份描述")

    def handle(self, *args, **options):
        try:
            name = (
                options["name"]
                or f"命令行备份 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            description = options["description"] or "通过命令行创建的备份"

            self.stdout.write(self.style.SUCCESS("开始创建备份..."))

            # 创建备份
            backup = BackupService.create_backup(name, description)

            # 备份媒体文件
            media_backup_path = BackupService.backup_media_files(backup)

            self.stdout.write(
                self.style.SUCCESS(
                    f"备份创建成功！\n备份ID: {backup.id}\n媒体文件备份路径: {media_backup_path}"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"备份创建失败：{str(e)}"))
