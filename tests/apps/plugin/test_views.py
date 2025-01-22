import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.plugin.models import Plugin

@pytest.mark.django_db
@pytest.mark.integration
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
            name='test-plugin',
            description='A test plugin',
            version='1.0.0',
            enabled=False,
            config={'key': 'value'}
        )

    def test_list_plugins(self, admin_client):
        """测试管理员获取插件列表"""
        url = reverse('plugin:list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert isinstance(response.data['data'], list)

    def test_list_plugins_forbidden(self, auth_client):
        """测试普通用户无法获取插件列表"""
        url = reverse('plugin:list')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "您没有执行该操作的权限" in str(response.data['detail'])

    def test_install_plugin(self, admin_client):
        """测试安装插件"""
        url = reverse('plugin:install')
        data = {
            'name': 'test-plugin',
            'version': '1.0.0'
        }
        response = admin_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200

    def test_install_plugin_forbidden(self, auth_client):
        """测试普通用户无法安装插件"""
        url = reverse('plugin:install')
        data = {
            'name': 'test-plugin',
            'version': '1.0.0'
        }
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "您没有执行该操作的权限" in str(response.data['detail'])

    def test_install_plugin_invalid(self, admin_client):
        """测试安装无效插件"""
        url = reverse('plugin:install')
        # 缺少必填字段 version
        data = {'name': 'test-plugin'}
        response = admin_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert response.data['message'] == "安装插件失败"
        assert 'version' in str(response.data['data']['errors'])

    def test_uninstall_plugin(self, admin_client, test_plugin):
        """测试卸载插件"""
        url = reverse('plugin:uninstall', kwargs={'plugin_id': test_plugin.name})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['message'] == "插件已卸载"
        assert not Plugin.objects.filter(name=test_plugin.name).exists()

    def test_uninstall_plugin_forbidden(self, auth_client, test_plugin):
        """测试普通用户无法卸载插件"""
        url = reverse('plugin:uninstall', kwargs={'plugin_id': test_plugin.name})
        response = auth_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "您没有执行该操作的权限" in str(response.data['detail'])

    def test_enable_plugin(self, admin_client, test_plugin):
        """测试启用插件"""
        url = reverse('plugin:enable', kwargs={'plugin_id': test_plugin.name})
        response = admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['message'] == "插件已启用"
        test_plugin.refresh_from_db()
        assert test_plugin.enabled

    def test_enable_nonexistent_plugin(self, admin_client):
        """测试启用不存在的插件"""
        url = reverse('plugin:enable', kwargs={'plugin_id': 'nonexistent'})
        response = admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 404
        assert response.data['message'] == "插件不存在"

    def test_disable_plugin(self, admin_client, test_plugin):
        """测试禁用插件"""
        test_plugin.enabled = True
        test_plugin.save()
        
        url = reverse('plugin:disable', kwargs={'plugin_id': test_plugin.name})
        response = admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['message'] == "插件已禁用"
        test_plugin.refresh_from_db()
        assert not test_plugin.enabled

    def test_disable_nonexistent_plugin(self, admin_client):
        """测试禁用不存在的插件"""
        url = reverse('plugin:disable', kwargs={'plugin_id': 'nonexistent'})
        response = admin_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 404
        assert response.data['message'] == "插件不存在"

    def test_update_plugin_settings(self, admin_client, test_plugin):
        """测试更新插件配置"""
        url = reverse('plugin:settings', kwargs={'plugin_id': test_plugin.name})
        data = {
            'config': {
                'setting1': 'value1',
                'setting2': 'value2'
            }
        }
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['config'] == data['config']
        test_plugin.refresh_from_db()
        assert test_plugin.config == data['config']

    def test_update_nonexistent_plugin_settings(self, admin_client):
        """测试更新不存在的插件配置"""
        url = reverse('plugin:settings', kwargs={'plugin_id': 'nonexistent'})
        data = {
            'config': {
                'setting1': 'value1',
                'setting2': 'value2'
            }
        }
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert response.data['message'] == "更新配置失败"

    def test_get_plugin_settings(self, admin_client, test_plugin):
        """测试获取插件配置"""
        url = reverse('plugin:settings', kwargs={'plugin_id': test_plugin.name})
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 200
        assert response.data['data']['config'] == test_plugin.config

    def test_get_plugin_settings_forbidden(self, auth_client, test_plugin):
        """测试普通用户无法获取插件配置"""
        url = reverse('plugin:settings', kwargs={'plugin_id': test_plugin.name})
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "您没有执行该操作的权限" in str(response.data['detail'])

    def test_update_plugin_settings_forbidden(self, auth_client, test_plugin):
        """测试普通用户无法更新插件配置"""
        url = reverse('plugin:settings', kwargs={'plugin_id': test_plugin.name})
        data = {'config': {'key': 'new_value'}}
        response = auth_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "您没有执行该操作的权限" in str(response.data['detail'])

    def test_update_plugin_settings_invalid(self, admin_client, test_plugin):
        """测试更新无效的插件配置"""
        url = reverse('plugin:settings', kwargs={'plugin_id': test_plugin.name})
        # config 必须是字典类型
        data = {'config': 'invalid'}
        response = admin_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 400
        assert response.data['message'] == "更新配置失败"
        assert 'config' in str(response.data['data']['errors']) 