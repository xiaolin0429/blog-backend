import pytest
from django.urls import reverse
from rest_framework import status

from apps.post.models import Tag


@pytest.mark.django_db
class TestTagViews:
    def test_list_tags_authenticated(self, auth_client):
        url = reverse("post:tag_list")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"]["results"], list)
        assert "count" in response.data["data"]

    def test_list_tags_unauthenticated(self, api_client):
        """测试未认证用户获取标签列表"""
        response = api_client.get(reverse("post:tag_list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert "results" in response.data["data"]

    def test_search_tags(self, auth_client, tag):
        url = reverse("post:tag_list")
        response = auth_client.get(f"{url}?search={tag.name}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"]["results"], list)
        assert len(response.data["data"]["results"]) == 1
        assert response.data["data"]["results"][0]["name"] == tag.name

    def test_create_tag(self, auth_client):
        url = reverse("post:tag_list")
        data = {"name": "Test Tag", "description": "Test Description"}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]
        assert response.data["data"]["description"] == data["description"]

    def test_create_tag_empty_name(self, auth_client):
        url = reverse("post:tag_list")
        data = {"name": ""}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert response.data["message"] == "标签名称不能为空"

    def test_create_tag_invalid_length(self, auth_client):
        url = reverse("post:tag_list")
        data = {"name": "a"}  # Too short
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert response.data["message"] == "标签名称长度必须在2-50个字符之间"

        data = {"name": "a" * 51}  # Too long
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert response.data["message"] == "标签名称长度必须在2-50个字符之间"

    def test_create_tag_duplicate_name(self, auth_client, tag):
        url = reverse("post:tag_list")
        data = {"name": tag.name}
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 409
        assert response.data["message"] == "标签名称已存在"

    def test_update_tag(self, auth_client, tag):
        url = reverse("post:tag_detail", kwargs={"pk": tag.id})
        data = {"name": "Updated Tag", "description": "Updated Description"}
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]
        assert response.data["data"]["description"] == data["description"]

    def test_update_nonexistent_tag(self, auth_client):
        url = reverse("post:tag_detail", kwargs={"pk": 999})
        data = {"name": "Updated Tag", "description": "Updated Description"}
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "标签不存在"

    def test_delete_tag(self, auth_client, tag):
        url = reverse("post:tag_detail", kwargs={"pk": tag.id})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["message"] == "删除成功"

    def test_delete_nonexistent_tag(self, auth_client):
        url = reverse("post:tag_detail", kwargs={"pk": 999})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "标签不存在"

    def test_batch_create_tags(self, auth_client):
        url = reverse("post:tag_batch_create")
        data = [
            {"name": "Tag 1", "description": "Description 1"},
            {"name": "Tag 2", "description": "Description 2"},
            {"name": "Tag 3", "description": "Description 3"},
        ]
        response = auth_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert len(response.data["data"]) == 3
        for i, tag in enumerate(response.data["data"]):
            assert tag["name"] == data[i]["name"]
            assert tag["description"] == data[i]["description"]

    def test_batch_create_tags_with_invalid_data(self, auth_client):
        url = reverse("post:tag_batch_create")
        data = [
            {"name": "", "description": "Description 1"},
            {"name": "a", "description": "Description 2"},
            {"name": "a" * 51, "description": "Description 3"},
        ]
        response = auth_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert "标签名称" in response.data["message"]

    def test_list_tags_with_pagination(self, auth_client):
        """测试标签列表分页"""
        # 创建11个标签
        for i in range(11):
            Tag.objects.create(name=f"Tag {i}")

        url = reverse("post:tag_list")
        response = auth_client.get(f"{url}?page=1&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert len(response.data["data"]["results"]) == 10
        assert response.data["data"]["count"] == 11

        # 测试第二页
        response = auth_client.get(f"{url}?page=2&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]["results"]) == 1

    def test_list_tags_ordering(self, auth_client):
        """测试标签列表排序"""
        Tag.objects.create(name="Tag B")
        Tag.objects.create(name="Tag A")
        Tag.objects.create(name="Tag C")

        url = reverse("post:tag_list")
        response = auth_client.get(f"{url}?ordering=name")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        results = response.data["data"]["results"]
        assert results[0]["name"] == "Tag A"
        assert results[1]["name"] == "Tag B"
        assert results[2]["name"] == "Tag C"

    def test_create_tag_unauthenticated(self, client):
        """测试未认证用户创建标签"""
        url = reverse("post:tag_list")
        data = {"name": "Test Tag"}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "您没有执行该操作的权限" in str(response.data["detail"])

    def test_get_tag_detail(self, auth_client, tag):
        """测试获取标签详情"""
        url = reverse("post:tag_detail", kwargs={"pk": tag.id})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == tag.name

    def test_update_tag_duplicate_name(self, auth_client, tag):
        """测试更新标签为重复名称"""
        # 创建另一个标签
        other_tag = Tag.objects.create(name="Other Tag")

        url = reverse("post:tag_detail", kwargs={"pk": other_tag.id})
        data = {"name": tag.name}  # 使用已存在的标签名称
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 409
        assert response.data["message"] == "标签名称已存在"

    def test_update_tag_unauthenticated(self, client, tag):
        """测试未认证用户更新标签"""
        url = reverse("post:tag_detail", kwargs={"pk": tag.id})
        data = {"name": "Updated Tag"}
        response = client.put(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "您没有执行该操作的权限" in str(response.data["detail"])

    def test_delete_tag_unauthenticated(self, client, tag):
        """测试未认证用户删除标签"""
        url = reverse("post:tag_detail", kwargs={"pk": tag.id})
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "您没有执行该操作的权限" in str(response.data["detail"])

    def test_batch_create_tags_with_duplicate(self, auth_client, tag):
        """测试批量创建包含重复名称的标签"""
        url = reverse("post:tag_batch_create")
        data = [
            {"name": "New Tag 1"},
            {"name": tag.name},  # 使用已存在的标签名称
            {"name": "New Tag 2"},
        ]
        response = auth_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 409
        assert response.data["message"] == "标签名称已存在"

    def test_batch_create_tags_unauthenticated(self, api_client):
        """测试未认证用户批量创建标签"""
        data = [{"name": "Tag A"}, {"name": "Tag B"}]
        response = api_client.post(
            reverse("post:tag_batch_create"), data=data, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data
        assert response.data["detail"] == "身份认证信息未提供。"
