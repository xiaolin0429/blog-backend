from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OverviewConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.overview"
    verbose_name = _("系统概览")
