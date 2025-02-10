from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from apps.backup.models import Backup
from apps.backup.services import BackupService


class Command(BaseCommand):
    help = "从指定的备份恢复数据"

    def add_arguments(self, parser):
        parser.add_argument("backup_id", type=int, help="要恢复的备份ID")

    def handle(self, *args, **options):
        try:
            backup_id = options["backup_id"]

            try:
                backup = Backup.objects.get(id=backup_id)
            except Backup.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"找不到ID为 {backup_id} 的备份"))
                return

            self.stdout.write(self.style.WARNING("警告：恢复操作将清空当前数据！"))
            self.stdout.write(f'即将从备份 "{backup.name}" 恢复数据')

            confirm = input("是否继续？[y/N] ")
            if confirm.lower() != "y":
                self.stdout.write(self.style.SUCCESS("操作已取消"))
                return

            self.stdout.write(self.style.SUCCESS("开始恢复数据..."))
            BackupService.restore_from_backup(backup)
            self.stdout.write(self.style.SUCCESS("数据恢复成功！"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"恢复失败：{str(e)}"))
