from django.urls import reverse

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.post.models import Category, Post


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
    def grandchild_category(self, child_category):
        return Category.objects.create(
            name="Grandchild Category",
            description="A grandchild category",
            parent=child_category,
        )

    @pytest.fixture
    def category(self):
        return Category.objects.create(
            name="Test Category", description="A test category"
        )

    @pytest.fixture
    def auth_client_non_staff(self, api_client, user_factory):
        """返回一个普通用户的认证客户端"""
        user = user_factory(is_staff=False)
        api_client.force_authenticate(user=user)
        return api_client

    def test_list_categories_authenticated(self, auth_client, parent_category, child_category):
        """测试已认证用户获取分类列表"""
        response = auth_client.get(reverse("post:category_list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"], list)
        # 只返回顶级分类
        assert all(category["parent"] is None for category in response.data["data"])
        # 检查子分类在children字段中
        parent_in_response = next(
            (cat for cat in response.data["data"] if cat["id"] == parent_category.id),
            None
        )
        assert parent_in_response is not None
        assert len(parent_in_response["children"]) > 0
        assert parent_in_response["children"][0]["id"] == child_category.id

    def test_list_categories_unauthenticated(self, client, parent_category, child_category):
        """测试未认证用户获取分类列表"""
        response = client.get(reverse("post:category_list"))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"], list)
        # 只返回顶级分类
        assert all(category["parent"] is None for category in response.data["data"])

    def test_filter_categories_by_parent(self, auth_client, parent_category, child_category):
        """测试按父分类筛选"""
        response = auth_client.get(
            reverse("post:category_list"), {"parent": parent_category.id}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"], list)
        # 只返回直接子分类
        assert all(category["parent"] == parent_category.id for category in response.data["data"])

    def test_category_level(self, auth_client, parent_category, child_category, grandchild_category):
        """测试分类层级"""
        # 获取顶级分类
        response = auth_client.get(reverse("post:category_list"))
        assert response.status_code == status.HTTP_200_OK
        parent_in_response = next(
            (cat for cat in response.data["data"] if cat["id"] == parent_category.id),
            None
        )
        assert parent_in_response is not None
        assert parent_in_response["level"] == 0

        # 检查子分类层级
        child_in_response = parent_in_response["children"][0]
        assert child_in_response["level"] == 1

        # 检查孙分类层级
        grandchild_in_response = child_in_response["children"][0]
        assert grandchild_in_response["level"] == 2

    def test_search_categories(self, auth_client, parent_category, child_category):
        """测试搜索分类"""
        response = auth_client.get(
            reverse("post:category_list"), {"search": parent_category.name}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"], list)
        assert len(response.data["data"]) > 0
        # 搜索时应该只返回匹配的顶级分类
        found_category = next(
            (cat for cat in response.data["data"] if cat["name"] == parent_category.name),
            None
        )
        assert found_category is not None

    def test_create_category(self, auth_client):
        """测试创建分类"""
        data = {"name": "New Test Category"}
        response = auth_client.post(reverse("post:category_list"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]
        assert response.data["data"]["level"] == 0
        assert "children" in response.data["data"]

    def test_create_category_with_parent(self, auth_client, parent_category):
        """测试创建子分类"""
        data = {"name": "New Child Category", "parent": parent_category.id}
        response = auth_client.post(reverse("post:category_list"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]
        assert response.data["data"]["parent"] == parent_category.id
        assert response.data["data"]["level"] == 1
        assert "children" in response.data["data"]

    def test_quick_create_category(self, auth_client):
        """测试快速创建分类"""
        data = {"name": "Quick Category"}
        response = auth_client.post(reverse("post:category_quick_create"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]
        assert response.data["data"]["parent"] is None

    def test_quick_create_category_with_parent(self, auth_client, parent_category):
        """测试快速创建子分类"""
        data = {"name": "Quick Child Category", "parent": parent_category.id}
        response = auth_client.post(reverse("post:category_quick_create"), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]
        assert response.data["data"]["parent"] == parent_category.id
        assert response.data["data"]["parent_name"] == parent_category.name

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

    def test_update_category(self, auth_client, category, user_factory):
        """测试更新分类"""
        # 设置用户为管理员
        user = user_factory(is_staff=True)
        auth_client.force_authenticate(user=user)
        
        data = {"name": "Updated Category"}
        response = auth_client.put(
            reverse("post:category_detail", args=[category.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["name"] == data["name"]

    def test_update_nonexistent_category(self, auth_client, user_factory):
        """测试更新不存在的分类"""
        # 设置用户为管理员
        user = user_factory(is_staff=True)
        auth_client.force_authenticate(user=user)
        
        data = {"name": "Updated Category"}
        response = auth_client.put(reverse("post:category_detail", args=[999]), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "分类不存在"

    def test_delete_category(self, auth_client, category, user_factory):
        """测试删除分类"""
        # 设置用户为管理员
        user = user_factory(is_staff=True)
        auth_client.force_authenticate(user=user)
        
        response = auth_client.delete(
            reverse("post:category_detail", args=[category.id])
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["message"] == "删除成功"
        assert response.data["data"] is None

    def test_delete_nonexistent_category(self, auth_client, user_factory):
        """测试删除不存在的分类"""
        # 设置用户为管理员
        user = user_factory(is_staff=True)
        auth_client.force_authenticate(user=user)
        
        response = auth_client.delete(reverse("post:category_detail", args=[999]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "分类不存在"

    def test_delete_category_with_posts(self, auth_client, category, post_factory, user_factory):
        """测试删除有关联文章的分类"""
        # 设置用户为管理员
        user = user_factory(is_staff=True)
        auth_client.force_authenticate(user=user)
        
        # 创建一篇关联到该分类的文章
        post = post_factory(category=category)
        
        response = auth_client.delete(
            reverse("post:category_detail", args=[category.id])
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 422
        assert "存在关联文章" in response.data["message"]
        # 确认分类未被删除
        assert Category.objects.filter(id=category.id).exists()

    def test_delete_category_with_children(self, auth_client, category, user_factory):
        """测试删除有子分类的分类"""
        # 设置用户为管理员
        user = user_factory(is_staff=True)
        auth_client.force_authenticate(user=user)
        
        # 创建一个子分类
        child_category = Category.objects.create(
            name="Child Category",
            parent=category
        )
        
        response = auth_client.delete(
            reverse("post:category_detail", args=[category.id])
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 422
        assert "存在子分类" in response.data["message"]
        # 确认分类未被删除
        assert Category.objects.filter(id=category.id).exists()
        assert Category.objects.filter(id=child_category.id).exists()

    def test_delete_category_with_children_and_posts(self, auth_client, category, post_factory, user_factory):
        """测试删除有子分类且子分类有关联文章的分类"""
        # 设置用户为管理员
        user = user_factory(is_staff=True)
        auth_client.force_authenticate(user=user)
        
        # 创建一个子分类
        child_category = Category.objects.create(
            name="Child Category",
            parent=category
        )
        # 创建一篇关联到子分类的文章
        post = post_factory(category=child_category)
        
        response = auth_client.delete(
            reverse("post:category_detail", args=[category.id])
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 422
        assert "存在子分类" in response.data["message"]
        # 确认分类未被删除
        assert Category.objects.filter(id=category.id).exists()
        assert Category.objects.filter(id=child_category.id).exists()

    def test_delete_category_unauthorized(self, client, category):
        """测试未认证用户删除分类"""
        response = client.delete(
            reverse("post:category_detail", args=[category.id])
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "身份认证信息未提供" in str(response.data["detail"])
        # 确认分类未被删除
        assert Category.objects.filter(id=category.id).exists()

    def test_delete_category_forbidden(self, auth_client_non_staff, category):
        """测试非管理员用户删除分类"""
        response = auth_client_non_staff.delete(
            reverse("post:category_detail", args=[category.id])
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 403
        assert "权限不足" in response.data["message"]
        # 确认分类未被删除
        assert Category.objects.filter(id=category.id).exists()
