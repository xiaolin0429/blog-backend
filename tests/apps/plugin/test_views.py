from django.urls import reverse

import allure
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.plugin.models import Plugin


@allure.epic("插件管理")
@allure.feature("插件操作")
@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.plugin
class TestPluginViews:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def admin_client(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        return api_client

    @pytest.fixture
    def auth_client(self, api_client, user):
        api_client.force_authenticate(user=user)
        return api_client

    @pytest.fixture
    def test_plugin(self):
        return Plugin.objects.create(
            name="test-plugin",
            description="A test plugin",
            version="1.0.0",
            enabled=False,
            config={"key": "value"},
        )

    @allure.story("插件列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试管理员获取插件列表的功能")
    @pytest.mark.high
    def test_list_plugins(self, admin_client):
        """测试管理员获取插件列表"""
        with allure.step("发送获取插件列表请求"):
            url = reverse("plugin:list")
            response = admin_client.get(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert isinstance(response.data["data"], list)

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("测试普通用户无法获取插件列表")
    @pytest.mark.security
    def test_list_plugins_forbidden(self, auth_client):
        """测试普通用户无法获取插件列表"""
        with allure.step("普通用户尝试获取插件列表"):
            url = reverse("plugin:list")
            response = auth_client.get(url)

        with allure.step("验证权限被拒绝"):
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "您没有执行该操作的权限" in str(response.data["detail"])

    @allure.story("插件安装")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试管理员安装插件的功能")
    @pytest.mark.high
    def test_install_plugin(self, admin_client):
        """测试安装插件"""
        with allure.step("发送安装插件请求"):
            url = reverse("plugin:install")
            data = {"name": "test-plugin", "version": "1.0.0"}
            response = admin_client.post(url, data)

        with allure.step("验证安装结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("测试普通用户无法安装插件")
    @pytest.mark.security
    def test_install_plugin_forbidden(self, auth_client):
        """测试普通用户无法安装插件"""
        with allure.step("普通用户尝试安装插件"):
            url = reverse("plugin:install")
            data = {"name": "test-plugin", "version": "1.0.0"}
            response = auth_client.post(url, data)

        with allure.step("验证权限被拒绝"):
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "您没有执行该操作的权限" in str(response.data["detail"])

    @allure.story("插件安装")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试安装无效插件时的错误处理")
    @pytest.mark.medium
    def test_install_plugin_invalid(self, admin_client):
        """测试安装无效插件"""
        with allure.step("发送无效的插件安装请求"):
            url = reverse("plugin:install")
            data = {"name": "test-plugin"}  # 缺少必填字段 version
            response = admin_client.post(url, data)

        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert response.data["message"] == "安装插件失败"
            assert "version" in str(response.data["data"]["errors"])

    @allure.story("插件卸载")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试管理员卸载插件的功能")
    @pytest.mark.high
    def test_uninstall_plugin(self, admin_client, test_plugin):
        """测试卸载插件"""
        with allure.step("发送卸载插件请求"):
            url = reverse("plugin:uninstall", kwargs={"plugin_id": test_plugin.name})
            response = admin_client.delete(url)

        with allure.step("验证卸载结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["message"] == "插件已卸载"
            assert not Plugin.objects.filter(name=test_plugin.name).exists()

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("测试普通用户无法卸载插件")
    @pytest.mark.security
    def test_uninstall_plugin_forbidden(self, auth_client, test_plugin):
        """测试普通用户无法卸载插件"""
        with allure.step("普通用户尝试卸载插件"):
            url = reverse("plugin:uninstall", kwargs={"plugin_id": test_plugin.name})
            response = auth_client.delete(url)

        with allure.step("验证权限被拒绝"):
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "您没有执行该操作的权限" in str(response.data["detail"])

    @allure.story("插件启用")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试管理员启用插件的功能")
    @pytest.mark.high
    def test_enable_plugin(self, admin_client, test_plugin):
        """测试启用插件"""
        with allure.step("发送启用插件请求"):
            url = reverse("plugin:enable", kwargs={"plugin_id": test_plugin.name})
            response = admin_client.post(url)

        with allure.step("验证启用结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["message"] == "插件已启用"
            test_plugin.refresh_from_db()
            assert test_plugin.enabled

    @allure.story("插件启用")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试启用不存在的插件时的错误处理")
    @pytest.mark.medium
    def test_enable_nonexistent_plugin(self, admin_client):
        """测试启用不存在的插件"""
        with allure.step("尝试启用不存在的插件"):
            url = reverse("plugin:enable", kwargs={"plugin_id": "nonexistent"})
            response = admin_client.post(url)

        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert response.data["message"] == "插件不存在"

    @allure.story("插件禁用")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试管理员禁用插件的功能")
    @pytest.mark.high
    def test_disable_plugin(self, admin_client, test_plugin):
        """测试禁用插件"""
        with allure.step("准备已启用的插件"):
            test_plugin.enabled = True
            test_plugin.save()

        with allure.step("发送禁用插件请求"):
            url = reverse("plugin:disable", kwargs={"plugin_id": test_plugin.name})
            response = admin_client.post(url)

        with allure.step("验证禁用结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["message"] == "插件已禁用"
            test_plugin.refresh_from_db()
            assert not test_plugin.enabled

    @allure.story("插件禁用")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试禁用不存在的插件时的错误处理")
    @pytest.mark.medium
    def test_disable_nonexistent_plugin(self, admin_client):
        """测试禁用不存在的插件"""
        with allure.step("尝试禁用不存在的插件"):
            url = reverse("plugin:disable", kwargs={"plugin_id": "nonexistent"})
            response = admin_client.post(url)

        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert response.data["message"] == "插件不存在"

    @allure.story("插件配置")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试管理员更新插件配置的功能")
    @pytest.mark.high
    def test_update_plugin_settings(self, admin_client, test_plugin):
        """测试更新插件配置"""
        with allure.step("发送更新配置请求"):
            url = reverse("plugin:settings", kwargs={"plugin_id": test_plugin.name})
            data = {"config": {"setting1": "value1", "setting2": "value2"}}
            response = admin_client.put(url, data, format="json")

        with allure.step("验证更新结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["config"] == data["config"]
            test_plugin.refresh_from_db()
            assert test_plugin.config == data["config"]

    @allure.story("插件配置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试更新不存在的插件配置时的错误处理")
    @pytest.mark.medium
    def test_update_nonexistent_plugin_settings(self, admin_client):
        """测试更新不存在的插件配置"""
        with allure.step("尝试更新不存在插件的配置"):
            url = reverse("plugin:settings", kwargs={"plugin_id": "nonexistent"})
            data = {"config": {"setting1": "value1", "setting2": "value2"}}
            response = admin_client.put(url, data, format="json")

        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert response.data["message"] == "更新配置失败"

    @allure.story("插件配置")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试管理员获取插件配置的功能")
    @pytest.mark.high
    def test_get_plugin_settings(self, admin_client, test_plugin):
        """测试获取插件配置"""
        with allure.step("发送获取配置请求"):
            url = reverse("plugin:settings", kwargs={"plugin_id": test_plugin.name})
            response = admin_client.get(url)

        with allure.step("验证获取结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["config"] == test_plugin.config

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("测试普通用户无法获取插件配置")
    @pytest.mark.security
    def test_get_plugin_settings_forbidden(self, auth_client, test_plugin):
        """测试普通用户无法获取插件配置"""
        with allure.step("普通用户尝试获取插件配置"):
            url = reverse("plugin:settings", kwargs={"plugin_id": test_plugin.name})
            response = auth_client.get(url)

        with allure.step("验证权限被拒绝"):
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "您没有执行该操作的权限" in str(response.data["detail"])

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("测试普通用户无法更新插件配置")
    @pytest.mark.security
    def test_update_plugin_settings_forbidden(self, auth_client, test_plugin):
        """测试普通用户无法更新插件配置"""
        with allure.step("普通用户尝试更新插件配置"):
            url = reverse("plugin:settings", kwargs={"plugin_id": test_plugin.name})
            data = {"config": {"key": "new_value"}}
            response = auth_client.put(url, data, format="json")

        with allure.step("验证权限被拒绝"):
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "您没有执行该操作的权限" in str(response.data["detail"])

    @allure.story("插件配置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试更新无效的插件配置时的错误处理")
    @pytest.mark.medium
    def test_update_plugin_settings_invalid(self, admin_client, test_plugin):
        """测试更新无效的插件配置"""
        with allure.step("发送无效的配置更新请求"):
            url = reverse("plugin:settings", kwargs={"plugin_id": test_plugin.name})
            data = {"config": "invalid"}  # config 必须是字典类型
            response = admin_client.put(url, data, format="json")

        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert response.data["message"] == "更新配置失败"
            assert "config" in str(response.data["data"]["errors"])
