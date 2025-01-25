import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.post.models import Category


@pytest.mark.django_db
@pytest.mark.integration
class TestCategoryViews:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def authenticated_client(self, api_client, normal_user):
        api_client.force_authenticate(user=normal_user)
        return api_client

    @pytest.fixture
    def parent_category(self):
        return Category.objects.create(
            name="Parent Category", description="A parent category"
        )

    @pytest.fixture
    def child_category(self, parent_category):
        return Category.objects.create(
            name="Child Category",
            description="A child category",
            parent=parent_category,
        )

    @pytest.fixture
    def category(self):
        return Category.objects.create(
            name="Test Category", description="A test category"
        )

    def test_list_categories_authenticated(self, auth_client):
        """测试已认证用户获取分类列表"""
        response = auth_client.get(reverse("post:category_list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"], list)

    def test_list_categories_unauthenticated(self, client):
        """测试未认证用户无法获取分类列表"""
        response = client.get(reverse("post:category_list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"], list)

    def test_filter_categories_by_parent(self, auth_client, parent_category):
        """测试按父分类筛选"""
        response = auth_client.get(
            reverse("post:category_list"), {"parent": parent_category.id}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"], list)
        for category in response.data["data"]:
            assert category["parent"] == parent_category.id

    def test_search_categories(self, auth_client, parent_category):
        """测试搜索分类"""
        response = auth_client.get(
            reverse("post:category_list"), {"search": parent_category.name}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"], list)
        assert len(response.data["data"]) > 0
        assert any(
            category["name"] == parent_category.name
            for category in response.data["data"]
        )

    def test_create_category(self, auth_client):
        """测试创建分类"""
        data = {"name": "Test Category"}
        response = auth_client.post(reverse("post:category_list"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]

    def test_create_category_with_parent(self, auth_client, parent_category):
        """测试创建子分类"""
        data = {"name": "Child Category", "parent": parent_category.id}
        response = auth_client.post(reverse("post:category_list"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]
        assert response.data["data"]["parent"] == parent_category.id

    def test_quick_create_category(self, auth_client):
        """测试快速创建分类"""
        data = {"name": "Quick Category"}
        response = auth_client.post(reverse("post:category_quick_create"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]

    def test_quick_create_category_with_parent(self, auth_client, parent_category):
        """测试快速创建子分类"""
        data = {"name": "Quick Child Category", "parent": parent_category.id}
        response = auth_client.post(reverse("post:category_quick_create"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]
        assert response.data["data"]["parent"] == parent_category.id

    def test_quick_create_category_empty_name(self, auth_client):
        """测试快速创建分类时名称为空"""
        data = {"name": ""}
        response = auth_client.post(reverse("post:category_quick_create"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert response.data["message"] == "分类名称不能为空"

    def test_quick_create_category_invalid_length(self, auth_client):
        """测试快速创建分类时名称长度无效"""
        # Test too short name
        data = {"name": "a"}
        response = auth_client.post(reverse("post:category_quick_create"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert "分类名称长度" in response.data["message"]

        # Test too long name
        data = {"name": "a" * 51}
        response = auth_client.post(reverse("post:category_quick_create"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert "分类名称长度" in response.data["message"]

    def test_quick_create_category_duplicate_name(self, auth_client, category):
        """测试快速创建重复名称的分类"""
        response = auth_client.post(
            reverse("post:category_quick_create"), {"name": category.name}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 409
        assert response.data["message"] == "分类名称已存在"

    def test_update_category(self, auth_client, category):
        """测试更新分类"""
        data = {"name": "Updated Category"}
        response = auth_client.put(
            reverse("post:category_detail", args=[category.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]

    def test_update_nonexistent_category(self, auth_client):
        """测试更新不存在的分类"""
        data = {"name": "Updated Category"}
        response = auth_client.put(reverse("post:category_detail", args=[999]), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "分类不存在"

    def test_delete_category(self, auth_client, category):
        """测试删除分类"""
        response = auth_client.delete(
            reverse("post:category_detail", args=[category.id])
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 204
        assert response.data["message"] == "success"
        assert response.data["data"] is None

    def test_delete_nonexistent_category(self, auth_client):
        """测试删除不存在的分类"""
        response = auth_client.delete(reverse("post:category_detail", args=[999]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "分类不存在"
