from django.urls import reverse

import allure
import pytest
from rest_framework import status

from apps.post.models import Tag


@allure.epic("标签管理")
@allure.feature("标签API")
@pytest.mark.django_db
class TestTagViews:
    @allure.story("标签列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试已认证用户获取标签列表")
    @pytest.mark.high
    def test_list_tags_authenticated(self, auth_client):
        with allure.step("发送获取标签列表请求"):
            url = reverse("post:tag_list")
            response = auth_client.get(url)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert isinstance(response.data["data"]["results"], list)
            assert "count" in response.data["data"]

    @allure.story("标签列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试未认证用户获取标签列表")
    @pytest.mark.medium
    def test_list_tags_unauthenticated(self, api_client):
        """测试未认证用户获取标签列表"""
        with allure.step("发送获取标签列表请求"):
            response = api_client.get(reverse("post:tag_list"))
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert "results" in response.data["data"]

    @allure.story("标签搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试标签搜索功能")
    @pytest.mark.medium
    def test_search_tags(self, auth_client, tag):
        with allure.step("发送标签搜索请求"):
            url = reverse("post:tag_list")
            response = auth_client.get(f"{url}?search={tag.name}")
        
        with allure.step("验证搜索结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert isinstance(response.data["data"]["results"], list)
            assert len(response.data["data"]["results"]) == 1
            assert response.data["data"]["results"][0]["name"] == tag.name

    @allure.story("标签创建")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试创建新标签")
    @pytest.mark.high
    def test_create_tag(self, auth_client):
        with allure.step("发送创建标签请求"):
            url = reverse("post:tag_list")
            data = {"name": "Test Tag", "description": "Test Description"}
            response = auth_client.post(url, data)
        
        with allure.step("验证创建结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["name"] == data["name"]
            assert response.data["data"]["description"] == data["description"]

    @allure.story("标签创建")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试创建标签时名称为空的情况")
    @pytest.mark.medium
    def test_create_tag_empty_name(self, auth_client):
        with allure.step("发送空名称的创建请求"):
            url = reverse("post:tag_list")
            data = {"name": ""}
            response = auth_client.post(url, data)
        
        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert response.data["message"] == "标签名称不能为空"

    @allure.story("标签创建")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试创建标签时名称长度无效的情况")
    @pytest.mark.medium
    def test_create_tag_invalid_length(self, auth_client):
        with allure.step("测试名称过短"):
            url = reverse("post:tag_list")
            data = {"name": "a"}  # Too short
            response = auth_client.post(url, data)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert response.data["message"] == "标签名称长度必须在2-50个字符之间"

        with allure.step("测试名称过长"):
            data = {"name": "a" * 51}  # Too long
            response = auth_client.post(url, data)
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert response.data["message"] == "标签名称长度必须在2-50个字符之间"

    @allure.story("标签创建")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试创建重复名称的标签")
    @pytest.mark.medium
    def test_create_tag_duplicate_name(self, auth_client, tag):
        with allure.step("发送重复名称的创建请求"):
            url = reverse("post:tag_list")
            data = {"name": tag.name}
            response = auth_client.post(url, data)
        
        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 409
            assert response.data["message"] == "标签名称已存在"

    @allure.story("标签更新")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试更新标签信息")
    @pytest.mark.high
    def test_update_tag(self, auth_client, tag):
        with allure.step("发送更新标签请求"):
            url = reverse("post:tag_detail", kwargs={"pk": tag.id})
            data = {"name": "Updated Tag", "description": "Updated Description"}
            response = auth_client.put(url, data)
        
        with allure.step("验证更新结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["name"] == data["name"]
            assert response.data["data"]["description"] == data["description"]

    @allure.story("标签更新")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试更新不存在的标签")
    @pytest.mark.medium
    def test_update_nonexistent_tag(self, auth_client):
        with allure.step("发送更新不存在标签的请求"):
            url = reverse("post:tag_detail", kwargs={"pk": 999})
            data = {"name": "Updated Tag", "description": "Updated Description"}
            response = auth_client.put(url, data)
        
        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert response.data["message"] == "标签不存在"

    @allure.story("标签删除")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试删除标签")
    @pytest.mark.high
    def test_delete_tag(self, auth_client, tag):
        with allure.step("发送删除标签请求"):
            url = reverse("post:tag_detail", kwargs={"pk": tag.id})
            response = auth_client.delete(url)
        
        with allure.step("验证删除结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["message"] == "删除成功"

    @allure.story("标签删除")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试删除不存在的标签")
    @pytest.mark.medium
    def test_delete_nonexistent_tag(self, auth_client):
        with allure.step("发送删除不存在标签的请求"):
            url = reverse("post:tag_detail", kwargs={"pk": 999})
            response = auth_client.delete(url)
        
        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert response.data["message"] == "标签不存在"

    @allure.story("标签批量创建")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试批量创建标签")
    @pytest.mark.high
    def test_batch_create_tags(self, auth_client):
        with allure.step("发送批量创建标签请求"):
            url = reverse("post:tag_batch_create")
            data = [
                {"name": "Tag 1", "description": "Description 1"},
                {"name": "Tag 2", "description": "Description 2"},
                {"name": "Tag 3", "description": "Description 3"},
            ]
            response = auth_client.post(url, data, format="json")
        
        with allure.step("验证创建结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert len(response.data["data"]) == 3
            for i, tag in enumerate(response.data["data"]):
                assert tag["name"] == data[i]["name"]
                assert tag["description"] == data[i]["description"]

    @allure.story("标签批量创建")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试批量创建标签时包含无效数据")
    @pytest.mark.medium
    def test_batch_create_tags_with_invalid_data(self, auth_client):
        with allure.step("发送包含无效数据的批量创建请求"):
            url = reverse("post:tag_batch_create")
            data = [
                {"name": "", "description": "Description 1"},
                {"name": "a", "description": "Description 2"},
                {"name": "a" * 51, "description": "Description 3"},
            ]
            response = auth_client.post(url, data, format="json")
        
        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert "标签名称" in response.data["message"]

    @allure.story("标签列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试标签列表分页功能")
    @pytest.mark.medium
    def test_list_tags_with_pagination(self, auth_client):
        """测试标签列表分页"""
        with allure.step("创建测试数据"):
            # 创建11个标签
            for i in range(11):
                Tag.objects.create(name=f"Tag {i}")

        with allure.step("测试第一页"):
            url = reverse("post:tag_list")
            response = auth_client.get(f"{url}?page=1&page_size=10")
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert len(response.data["data"]["results"]) == 10
            assert response.data["data"]["count"] == 11

        with allure.step("测试第二页"):
            response = auth_client.get(f"{url}?page=2&page_size=10")
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data["data"]["results"]) == 1

    @allure.story("标签列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试标签列表排序功能")
    @pytest.mark.medium
    def test_list_tags_ordering(self, auth_client):
        """测试标签列表排序"""
        with allure.step("创建测试数据"):
            Tag.objects.create(name="Tag B")
            Tag.objects.create(name="Tag A")
            Tag.objects.create(name="Tag C")

        with allure.step("测试名称排序"):
            url = reverse("post:tag_list")
            response = auth_client.get(f"{url}?ordering=name")
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            results = response.data["data"]["results"]
            assert results[0]["name"] == "Tag A"
            assert results[1]["name"] == "Tag B"
            assert results[2]["name"] == "Tag C"

    @allure.story("标签创建")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试未认证用户创建标签")
    @pytest.mark.high
    def test_create_tag_unauthenticated(self, client):
        """测试未认证用户创建标签"""
        with allure.step("发送未认证的创建请求"):
            url = reverse("post:tag_list")
            data = {"name": "Test Tag"}
            response = client.post(url, data)
        
        with allure.step("验证权限错误"):
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "您没有执行该操作的权限" in str(response.data["detail"])

    @allure.story("标签详情")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试获取标签详情")
    @pytest.mark.medium
    def test_get_tag_detail(self, auth_client, tag):
        """测试获取标签详情"""
        with allure.step("发送获取标签详情请求"):
            url = reverse("post:tag_detail", kwargs={"pk": tag.id})
            response = auth_client.get(url)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["name"] == tag.name

    @allure.story("标签更新")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试更新标签为重复名称")
    @pytest.mark.medium
    def test_update_tag_duplicate_name(self, auth_client, tag):
        """测试更新标签为重复名称"""
        with allure.step("创建测试数据"):
            other_tag = Tag.objects.create(name="Other Tag")

        with allure.step("发送重复名称的更新请求"):
            url = reverse("post:tag_detail", kwargs={"pk": other_tag.id})
            data = {"name": tag.name}  # 使用已存在的标签名称
            response = auth_client.put(url, data)
        
        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 409
            assert response.data["message"] == "标签名称已存在"

    @allure.story("标签更新")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试未认证用户更新标签")
    @pytest.mark.high
    def test_update_tag_unauthenticated(self, client, tag):
        """测试未认证用户更新标签"""
        with allure.step("发送未认证的更新请求"):
            url = reverse("post:tag_detail", kwargs={"pk": tag.id})
            data = {"name": "Updated Tag"}
            response = client.put(url, data)
        
        with allure.step("验证权限错误"):
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "您没有执行该操作的权限" in str(response.data["detail"])

    @allure.story("标签删除")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试未认证用户删除标签")
    @pytest.mark.high
    def test_delete_tag_unauthenticated(self, client, tag):
        """测试未认证用户删除标签"""
        with allure.step("发送未认证的删除请求"):
            url = reverse("post:tag_detail", kwargs={"pk": tag.id})
            response = client.delete(url)
        
        with allure.step("验证权限错误"):
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "您没有执行该操作的权限" in str(response.data["detail"])

    @allure.story("标签批量创建")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试批量创建包含重复名称的标签")
    @pytest.mark.medium
    def test_batch_create_tags_with_duplicate(self, auth_client, tag):
        """测试批量创建包含重复名称的标签"""
        with allure.step("发送包含重复名称的批量创建请求"):
            url = reverse("post:tag_batch_create")
            data = [
                {"name": "New Tag 1"},
                {"name": tag.name},  # 使用已存在的标签名称
                {"name": "New Tag 2"},
            ]
            response = auth_client.post(url, data, format="json")
        
        with allure.step("验证错误响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 409
            assert response.data["message"] == "标签名称已存在"

    @allure.story("标签批量创建")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试未认证用户批量创建标签")
    @pytest.mark.high
    def test_batch_create_tags_unauthenticated(self, api_client):
        """测试未认证用户批量创建标签"""
        with allure.step("发送未认证的批量创建请求"):
            data = [{"name": "Tag A"}, {"name": "Tag B"}]
            response = api_client.post(
                reverse("post:tag_batch_create"), data=data, format="json"
            )
        
        with allure.step("验证权限错误"):
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "detail" in response.data
            assert response.data["detail"] == "身份认证信息未提供。"
