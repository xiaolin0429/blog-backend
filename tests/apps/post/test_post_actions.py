from django.urls import reverse

import pytest
from rest_framework import status

from apps.post.models import Post


@pytest.mark.django_db
class TestPostActions:
    def test_like_post(self, auth_client, post):
        """测试点赞文章"""
        url = reverse("post:post_like", kwargs={"pk": post.id})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert "文章不存在" in response.data["message"]

    def test_like_post_twice(self, auth_client, post):
        """测试重复点赞文章"""
        url = reverse("post:post_like", kwargs={"pk": post.id})
        auth_client.post(url)
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert "文章不存在" in response.data["message"]

    def test_like_nonexistent_post(self, auth_client):
        """测试点赞不存在的文章"""
        url = reverse("post:post_like", kwargs={"pk": 99999})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert "文章不存在" in response.data["message"]

    def test_view_post(self, client, post):
        """测试浏览文章"""
        url = reverse("post:post_view", kwargs={"pk": post.id})
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert "文章不存在" in response.data["message"]

    def test_view_post_multiple_times(self, client, post):
        """测试多次浏览文章"""
        url = reverse("post:post_view", kwargs={"pk": post.id})
        client.post(url)
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert "文章不存在" in response.data["message"]

    def test_view_nonexistent_post(self, client):
        """测试浏览不存在的文章"""
        url = reverse("post:post_view", kwargs={"pk": 99999})
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "文章不存在或未发布"

    def test_archive_post(self, auth_client, post):
        """测试归档文章"""
        url = reverse("post:post_archive", kwargs={"pk": post.id})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["status"] == "archived"
        post.refresh_from_db()
        assert post.status == "archived"

    def test_archive_nonexistent_post(self, auth_client):
        """测试归档不存在的文章"""
        url = reverse("post:post_archive", kwargs={"pk": 99999})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "文章不存在或无权限"

    def test_archive_other_user_post(self, auth_client, other_post):
        """测试归档其他用户的文章"""
        url = reverse("post:post_archive", kwargs={"pk": other_post.id})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "文章不存在或无权限"

    def test_archive_post_unauthenticated(self, client, post):
        """测试未认证用户归档文章"""
        url = reverse("post:post_archive", kwargs={"pk": post.id})
        response = client.post(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
