import allure
from django.urls import reverse

import pytest
from rest_framework import status

from apps.post.models import Category, Post, Tag
from tests.apps.post.factories import PostFactory, UserFactory


@allure.epic("文章管理")
@allure.feature("文章CRUD")
@pytest.mark.django_db
class TestPostCRUD:
    @allure.story("创建文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试已登录用户创建文章的功能")
    @pytest.mark.high
    def test_create_post(self, auth_client):
        with allure.step("准备创建文章数据"):
            url = reverse("post:post_list")
            data = {
                "title": "Test Post",
                "content": "Test content",
                "status": "published",  # 设置为已发布状态
            }
        
        with allure.step("发送创建文章请求"):
            response = auth_client.post(url, data)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["title"] == data["title"]
            assert response.data["data"]["content"] == data["content"]

    @allure.story("创建文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试未登录用户无法创建文章")
    @pytest.mark.high
    def test_create_post_unauthenticated(self, client):
        with allure.step("准备创建文章数据"):
            url = reverse("post:post_list")
            data = {"title": "Test Post", "content": "Test content"}
        
        with allure.step("发送创建文章请求"):
            response = client.post(url, data)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @allure.story("获取文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试获取单篇文章的详细信息")
    @pytest.mark.high
    def test_retrieve_post(self, auth_client, post):
        with allure.step("准备文章数据"):
            # 确保文章是已发布状态
            post.status = "published"
            post.save()

        with allure.step("发送获取文章请求"):
            url = reverse("post:post_detail", kwargs={"pk": post.id})
            response = auth_client.get(url)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["title"] == post.title
            assert response.data["data"]["content"] == post.content

    @allure.story("更新文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试更新文章的功能")
    @pytest.mark.high
    def test_update_post(self, auth_client, post):
        with allure.step("准备更新数据"):
            url = reverse("post:post_update", kwargs={"pk": post.id})
            data = {"title": "Updated Title", "content": "Updated content"}
        
        with allure.step("发送更新请求"):
            response = auth_client.put(url, data)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["title"] == data["title"]
            assert response.data["data"]["content"] == data["content"]

    @allure.story("更新文章")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试更新不存在的文章时的错误处理")
    @pytest.mark.medium
    def test_update_nonexistent_post(self, auth_client):
        with allure.step("准备更新数据"):
            url = reverse("post:post_update", kwargs={"pk": 999})
            data = {"title": "Updated Title", "content": "Updated content"}
        
        with allure.step("发送更新请求"):
            response = auth_client.put(url, data)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400  # 服务器返回400而不是404
            assert "更新文章失败" in response.data["message"]

    @allure.story("删除文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试删除文章的功能")
    @pytest.mark.high
    def test_delete_post(self, auth_client, post):
        with allure.step("发送删除请求"):
            url = reverse("post:post_delete", kwargs={"pk": post.id})
            response = auth_client.delete(url)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            post.refresh_from_db()
            assert post.is_deleted

    @allure.story("删除文章")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试删除不存在的文章时的错误处理")
    @pytest.mark.medium
    def test_delete_nonexistent_post(self, auth_client):
        with allure.step("发送删除请求"):
            url = reverse("post:post_delete", kwargs={"pk": 999})
            response = auth_client.delete(url)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404

    @allure.story("获取文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试获取文章详情的功能")
    @pytest.mark.high
    def test_get_post_detail(self, auth_client, post):
        with allure.step("准备文章数据"):
            # 确保文章是已发布状态
            post.status = "published"
            post.save()

        with allure.step("发送获取详情请求"):
            url = reverse("post:post_detail", kwargs={"pk": post.id})
            response = auth_client.get(url)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["title"] == post.title
            assert response.data["data"]["content"] == post.content

    @allure.story("更新文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试用户无法更新其他用户的文章")
    @pytest.mark.high
    def test_update_other_user_post(self, auth_client, other_post):
        with allure.step("准备更新数据"):
            url = reverse("post:post_update", kwargs={"pk": other_post.id})
            data = {"title": "Updated Title", "content": "Updated content"}
        
        with allure.step("发送更新请求"):
            response = auth_client.put(url, data)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400  # 服务器返回400
            assert "更新文章失败" in response.data["message"]

    @allure.story("删除文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试用户无法删除其他用户的文章")
    @pytest.mark.high
    def test_delete_other_user_post(self, auth_client, other_post):
        with allure.step("发送删除请求"):
            url = reverse("post:post_delete", kwargs={"pk": other_post.id})
            response = auth_client.delete(url)
        
        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404  # 服务器返回404
            assert "文章不存在或无权限删除" in response.data["message"]
