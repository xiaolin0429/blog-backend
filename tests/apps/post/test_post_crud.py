from django.urls import reverse

import pytest
from rest_framework import status

from apps.post.models import Category, Post, Tag


@pytest.mark.django_db
class TestPostCRUD:
    def test_create_post(self, auth_client):
        url = reverse("post:post_list")
        data = {
            "title": "Test Post",
            "content": "Test content",
            "status": "published",  # 设置为已发布状态
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["title"] == data["title"]
        assert response.data["data"]["content"] == data["content"]

    def test_create_post_unauthenticated(self, client):
        url = reverse("post:post_list")
        data = {"title": "Test Post", "content": "Test content"}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_post(self, auth_client, post):
        # 确保文章是已发布状态
        post.status = "published"
        post.save()

        url = reverse("post:post_detail", kwargs={"pk": post.id})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["title"] == post.title
        assert response.data["data"]["content"] == post.content

    def test_update_post(self, auth_client, post):
        url = reverse("post:post_update", kwargs={"pk": post.id})
        data = {"title": "Updated Title", "content": "Updated content"}
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["title"] == data["title"]
        assert response.data["data"]["content"] == data["content"]

    def test_update_nonexistent_post(self, auth_client):
        url = reverse("post:post_update", kwargs={"pk": 999})
        data = {"title": "Updated Title", "content": "Updated content"}
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400  # 服务器返回400而不是404
        assert "更新文章失败" in response.data["message"]

    def test_delete_post(self, auth_client, post):
        url = reverse("post:post_delete", kwargs={"pk": post.id})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        post.refresh_from_db()
        assert post.is_deleted

    def test_delete_nonexistent_post(self, auth_client):
        url = reverse("post:post_delete", kwargs={"pk": 999})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404

    def test_get_post_detail(self, auth_client, post):
        # 确保文章是已发布状态
        post.status = "published"
        post.save()

        url = reverse("post:post_detail", kwargs={"pk": post.id})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["title"] == post.title
        assert response.data["data"]["content"] == post.content

    def test_update_other_user_post(self, auth_client, other_post):
        url = reverse("post:post_update", kwargs={"pk": other_post.id})
        data = {"title": "Updated Title", "content": "Updated content"}
        response = auth_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400  # 服务器返回400
        assert "更新文章失败" in response.data["message"]

    def test_delete_other_user_post(self, auth_client, other_post):
        url = reverse("post:post_delete", kwargs={"pk": other_post.id})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404  # 服务器返回404
        assert "文章不存在或无权限删除" in response.data["message"]
