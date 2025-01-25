from django.urls import reverse

import pytest
from rest_framework import status

from apps.post.models import Post


@pytest.mark.django_db
class TestPostTrash:
    def test_list_trash_posts(self, auth_client, user):
        """测试获取回收站文章列表"""
        # 创建一些已删除的文章
        Post.objects.create(title="已删除文章1", content="内容1", author=user, is_deleted=True)
        Post.objects.create(title="已删除文章2", content="内容2", author=user, is_deleted=True)

        url = reverse("post:post_trash_list")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert len(response.data["data"]) == 2

    def test_list_trash_posts_empty(self, auth_client):
        """测试获取空的回收站列表"""
        url = reverse("post:post_trash_list")
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert len(response.data["data"]) == 0

    def test_restore_post(self, auth_client, user):
        """测试恢复已删除的文章"""
        post = Post.objects.create(
            title="已删除文章", content="内容", author=user, is_deleted=True
        )

        url = reverse("post:post_restore", kwargs={"pk": post.id})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["status"] == "restored"
        post.refresh_from_db()
        assert not post.is_deleted
        assert post.status == "draft"

    def test_restore_nonexistent_post(self, auth_client):
        """测试恢复不存在的文章"""
        url = reverse("post:post_restore", kwargs={"pk": 99999})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "文章不存在或无权限"

    def test_permanent_delete_post(self, auth_client, user):
        """测试永久删除文章"""
        post = Post.objects.create(
            title="已删除文章", content="内容", author=user, is_deleted=True
        )

        url = reverse("post:post_permanent_delete", kwargs={"pk": post.id})
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["message"] == "文章已永久删除"
        assert not Post.objects.filter(id=post.id).exists()

    def test_permanent_delete_nonexistent_post(self, auth_client):
        """测试永久删除不存在的文章"""
        url = reverse("post:post_permanent_delete", kwargs={"pk": 99999})
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "文章不存在或无权限"

    def test_empty_trash(self, auth_client, user):
        """测试清空回收站"""
        # 创建一些已删除的文章
        Post.objects.create(title="已删除文章1", content="内容1", author=user, is_deleted=True)
        Post.objects.create(title="已删除文章2", content="内容2", author=user, is_deleted=True)

        url = reverse("post:post_empty_trash")
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["message"] == "回收站已清空"
        assert not Post.objects.filter(is_deleted=True).exists()

    def test_empty_trash_unauthenticated(self, client):
        """测试未认证用户清空回收站"""
        url = reverse("post:post_empty_trash")
        response = client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
