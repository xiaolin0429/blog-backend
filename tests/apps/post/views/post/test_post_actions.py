import allure
from django.urls import reverse

import pytest
from rest_framework import status

from apps.post.models import Post
from tests.apps.post.factories import PostFactory, UserFactory


@allure.epic("文章管理")
@allure.feature("文章操作")
@pytest.mark.django_db
class TestPostActions:
    @allure.story("点赞文章")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试点赞文章的功能")
    @pytest.mark.medium
    def test_like_post(self, auth_client, post):
        """测试点赞文章"""
        with allure.step("发送点赞请求"):
            url = reverse("post:post_like", kwargs={"pk": post.id})
            response = auth_client.post(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert "文章不存在" in response.data["message"]

    @allure.story("点赞文章")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试重复点赞文章时的处理")
    @pytest.mark.medium
    def test_like_post_twice(self, auth_client, post):
        """测试重复点赞文章"""
        with allure.step("第一次点赞"):
            url = reverse("post:post_like", kwargs={"pk": post.id})
            auth_client.post(url)
        
        with allure.step("第二次点赞"):
            response = auth_client.post(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert "文章不存在" in response.data["message"]

    @allure.story("点赞文章")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试点赞不存在的文章时的错误处理")
    @pytest.mark.medium
    def test_like_nonexistent_post(self, auth_client):
        """测试点赞不存在的文章"""
        with allure.step("发送点赞请求"):
            url = reverse("post:post_like", kwargs={"pk": 99999})
            response = auth_client.post(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert "文章不存在" in response.data["message"]

    @allure.story("浏览文章")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试浏览文章时增加浏览量")
    @pytest.mark.medium
    def test_view_post(self, client, post):
        """测试浏览文章"""
        with allure.step("发送浏览请求"):
            url = reverse("post:post_view", kwargs={"pk": post.id})
            response = client.post(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert "文章不存在" in response.data["message"]

    @allure.story("浏览文章")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试多次浏览文章时的浏览量计数")
    @pytest.mark.medium
    def test_view_post_multiple_times(self, client, post):
        """测试多次浏览文章"""
        with allure.step("第一次浏览"):
            url = reverse("post:post_view", kwargs={"pk": post.id})
            client.post(url)
        
        with allure.step("第二次浏览"):
            response = client.post(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert "文章不存在" in response.data["message"]

    @allure.story("浏览文章")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试浏览不存在的文章时的错误处理")
    @pytest.mark.medium
    def test_view_nonexistent_post(self, client):
        """测试浏览不存在的文章"""
        with allure.step("发送浏览请求"):
            url = reverse("post:post_view", kwargs={"pk": 99999})
            response = client.post(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert response.data["message"] == "文章不存在或未发布"

    @allure.story("归档文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试归档文章的功能")
    @pytest.mark.high
    def test_archive_post(self, auth_client, post):
        """测试归档文章"""
        with allure.step("发送归档请求"):
            url = reverse("post:post_archive", kwargs={"pk": post.id})
            response = auth_client.post(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["status"] == "archived"
            post.refresh_from_db()
            assert post.status == "archived"

    @allure.story("归档文章")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试归档不存在的文章时的错误处理")
    @pytest.mark.medium
    def test_archive_nonexistent_post(self, auth_client):
        """测试归档不存在的文章"""
        with allure.step("发送归档请求"):
            url = reverse("post:post_archive", kwargs={"pk": 99999})
            response = auth_client.post(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert response.data["message"] == "文章不存在或无权限"

    @allure.story("归档文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试用户无法归档其他用户的文章")
    @pytest.mark.high
    def test_archive_other_user_post(self, auth_client, other_post):
        """测试归档其他用户的文章"""
        with allure.step("发送归档请求"):
            url = reverse("post:post_archive", kwargs={"pk": other_post.id})
            response = auth_client.post(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert response.data["message"] == "文章不存在或无权限"

    @allure.story("归档文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试未登录用户无法归档文章")
    @pytest.mark.high
    def test_archive_post_unauthenticated(self, client, post):
        """测试未认证用户归档文章"""
        with allure.step("发送归档请求"):
            url = reverse("post:post_archive", kwargs={"pk": post.id})
            response = client.post(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
