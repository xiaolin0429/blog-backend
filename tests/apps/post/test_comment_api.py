from django.urls import reverse

import pytest
from rest_framework import status

from apps.post.models import Comment, Post


@pytest.mark.django_db
class TestCommentAPI:
    def test_list_comments(self, auth_client, post, comment):
        response = auth_client.get(reverse("post:comment_list_create", args=[post.id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"], list)
        assert len(response.data["data"]) == 1

    def test_create_comment(self, auth_client, post):
        data = {"content": "Test comment"}
        response = auth_client.post(
            reverse("post:comment_list_create", args=[post.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["content"] == data["content"]

    def test_create_comment_with_invalid_post(self, auth_client):
        data = {"content": "Test comment"}
        response = auth_client.post(
            reverse("post:comment_list_create", args=[999]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 404
        assert response.data["message"] == "文章不存在"

    def test_create_comment_with_parent(self, auth_client, post, comment):
        data = {"content": "Test reply", "parent": comment.id}
        response = auth_client.post(
            reverse("post:comment_list_create", args=[post.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["content"] == data["content"]
        assert response.data["data"]["parent"] == comment.id

    def test_create_comment_with_invalid_parent(self, auth_client, post):
        data = {"content": "Test reply", "parent": 999}
        response = auth_client.post(
            reverse("post:comment_list_create", args=[post.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert response.data["message"] == "父评论不存在"

    def test_create_comment_with_empty_content(self, auth_client, post):
        data = {"content": ""}
        response = auth_client.post(
            reverse("post:comment_list_create", args=[post.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert response.data["message"] == "评论内容不能为空"

    def test_create_reply(self, auth_client, post, comment):
        data = {"content": "Test nested reply", "parent": comment.id}
        response = auth_client.post(
            reverse("post:comment_list_create", args=[post.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["content"] == data["content"]
        assert response.data["data"]["parent"] == comment.id

    def test_create_nested_reply(self, auth_client, post, reply):
        data = {"content": "Test nested reply", "parent": reply.id}
        response = auth_client.post(
            reverse("post:comment_list_create", args=[post.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert response.data["message"] == "不支持嵌套回复"

    def test_create_cross_post_reply(self, auth_client, post, other_post, comment):
        data = {"content": "Test cross post reply", "parent": comment.id}
        response = auth_client.post(
            reverse("post:comment_list_create", args=[other_post.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 400
        assert response.data["message"] == "不能跨文章回复评论"

    def test_update_comment(self, auth_client, comment):
        data = {"content": "Updated comment"}
        response = auth_client.put(
            reverse("post:comment_detail", args=[comment.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["data"]["content"] == data["content"]

    def test_update_other_user_comment(self, auth_client, other_user_comment):
        data = {"content": "Try to update other's comment"}
        response = auth_client.put(
            reverse("post:comment_detail", args=[other_user_comment.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 403
        assert response.data["message"] == "无权修改他人的评论"

    def test_delete_comment(self, auth_client, comment):
        response = auth_client.delete(reverse("post:comment_detail", args=[comment.id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert response.data["message"] == "删除成功"

    def test_delete_other_user_comment(self, auth_client, other_user_comment):
        response = auth_client.delete(
            reverse("post:comment_detail", args=[other_user_comment.id])
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 403
        assert response.data["message"] == "无权删除他人的评论"

    def test_anonymous_user_operations(self, client, post, comment):
        # Test list comments
        response = client.get(reverse("post:comment_list_create", args=[post.id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert isinstance(response.data["data"], list)

        # Test create comment
        data = {"content": "Test comment"}
        response = client.post(
            reverse("post:comment_list_create", args=[post.id]), data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 401
        assert response.data["message"] == "未登录用户无法评论"

        # Test update comment
        data = {"content": "Updated comment"}
        response = client.put(reverse("post:comment_detail", args=[comment.id]), data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 401
        assert response.data["message"] == "未登录用户无法修改评论"

        # Test delete comment
        response = client.delete(reverse("post:comment_detail", args=[comment.id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 401
        assert response.data["message"] == "未登录用户无法删除评论"
