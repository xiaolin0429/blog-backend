from django.urls import path

from . import views

app_name = "plugin"

urlpatterns = [
    # 插件管理
    path("", views.PluginListView.as_view(), name="list"),
    path("install/", views.PluginInstallView.as_view(), name="install"),
    path(
        "<str:plugin_id>/uninstall/",
        views.PluginUninstallView.as_view(),
        name="uninstall",
    ),
    path("<str:plugin_id>/enable/", views.PluginEnableView.as_view(), name="enable"),
    path("<str:plugin_id>/disable/", views.PluginDisableView.as_view(), name="disable"),
    path(
        "<str:plugin_id>/settings/", views.PluginSettingsView.as_view(), name="settings"
    ),
]
