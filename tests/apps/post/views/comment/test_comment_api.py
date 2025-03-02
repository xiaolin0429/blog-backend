from django.urls import reverse

import allure
import pytest
from rest_framework import status

from apps.post.models import Comment, Post
from tests.apps.post.factories import CommentFactory, PostFactory, UserFactory


@allure.epic("评论管理")
@allure.feature("文章评论")
@pytest.mark.django_db
@pytest.mark.comment
class TestCommentAPI:
    @allure.story("评论列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试获取文章评论列表")
    @pytest.mark.medium
    def test_list_comments(self, auth_client, post, comment):
        with allure.step("获取评论列表"):
            response = auth_client.get(
                reverse("post:comment_list_create", args=[post.id])
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert isinstance(response.data["data"], list)
            assert len(response.data["data"]) == 1

    @allure.story("创建评论")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试创建新评论")
    @pytest.mark.high
    def test_create_comment(self, auth_client, post):
        with allure.step("创建评论"):
            data = {"content": "Test comment"}
            response = auth_client.post(
                reverse("post:comment_list_create", args=[post.id]), data
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["content"] == data["content"]

    @allure.story("创建评论")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试对不存在的文章创建评论")
    @pytest.mark.medium
    def test_create_comment_with_invalid_post(self, auth_client):
        with allure.step("尝试对不存在的文章创建评论"):
            data = {"content": "Test comment"}
            response = auth_client.post(
                reverse("post:comment_list_create", args=[999]), data
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert response.data["message"] == "文章不存在"

    @allure.story("回复评论")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试回复已有评论")
    @pytest.mark.high
    def test_create_comment_with_parent(self, auth_client, post, comment):
        with allure.step("创建回复"):
            data = {"content": "Test reply", "parent": comment.id}
            response = auth_client.post(
                reverse("post:comment_list_create", args=[post.id]), data
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["content"] == data["content"]
            assert response.data["data"]["parent"] == comment.id

    @allure.story("回复评论")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试回复不存在的评论")
    @pytest.mark.medium
    def test_create_comment_with_invalid_parent(self, auth_client, post):
        with allure.step("尝试回复不存在的评论"):
            data = {"content": "Test reply", "parent": 999}
            response = auth_client.post(
                reverse("post:comment_list_create", args=[post.id]), data
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert response.data["message"] == "父评论不存在"

    @allure.story("创建评论")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试创建空内容的评论")
    @pytest.mark.medium
    def test_create_comment_with_empty_content(self, auth_client, post):
        with allure.step("尝试创建空内容的评论"):
            data = {"content": ""}
            response = auth_client.post(
                reverse("post:comment_list_create", args=[post.id]), data
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert response.data["message"] == "评论内容不能为空"

    @allure.story("回复评论")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试创建嵌套回复")
    @pytest.mark.high
    def test_create_nested_reply(self, auth_client, post, reply):
        with allure.step("尝试创建嵌套回复"):
            data = {"content": "Test nested reply", "parent": reply.id}
            response = auth_client.post(
                reverse("post:comment_list_create", args=[post.id]), data
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert response.data["message"] == "不支持嵌套回复"

    @allure.story("回复评论")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试跨文章回复评论")
    @pytest.mark.medium
    def test_create_cross_post_reply(self, auth_client, post, other_post, comment):
        with allure.step("尝试跨文章回复评论"):
            data = {"content": "Test cross post reply", "parent": comment.id}
            response = auth_client.post(
                reverse("post:comment_list_create", args=[other_post.id]), data
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert response.data["message"] == "不能跨文章回复评论"

    @allure.story("更新评论")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试更新评论内容")
    @pytest.mark.high
    def test_update_comment(self, auth_client, comment):
        with allure.step("更新评论"):
            data = {"content": "Updated comment"}
            response = auth_client.put(
                reverse("post:comment_detail", args=[comment.id]), data
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["content"] == data["content"]

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试更新他人的评论")
    @pytest.mark.security
    def test_update_other_user_comment(self, auth_client, other_user_comment):
        with allure.step("尝试更新他人的评论"):
            data = {"content": "Try to update other's comment"}
            response = auth_client.put(
                reverse("post:comment_detail", args=[other_user_comment.id]), data
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 403
            assert response.data["message"] == "无权修改他人的评论"

    @allure.story("删除评论")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试删除评论")
    @pytest.mark.high
    def test_delete_comment(self, auth_client, comment):
        with allure.step("删除评论"):
            response = auth_client.delete(
                reverse("post:comment_detail", args=[comment.id])
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["message"] == "删除成功"

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试删除他人的评论")
    @pytest.mark.security
    def test_delete_other_user_comment(self, auth_client, other_user_comment):
        with allure.step("尝试删除他人的评论"):
            response = auth_client.delete(
                reverse("post:comment_detail", args=[other_user_comment.id])
            )

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 403
            assert response.data["message"] == "无权删除他人的评论"

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试未登录用户的评论操作")
    @pytest.mark.security
    def test_anonymous_user_operations(self, client, post, comment):
        with allure.step("测试获取评论列表"):
            response = client.get(reverse("post:comment_list_create", args=[post.id]))
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert isinstance(response.data["data"], list)

        with allure.step("测试创建评论"):
            data = {"content": "Test comment"}
            response = client.post(
                reverse("post:comment_list_create", args=[post.id]), data
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 401
            assert response.data["message"] == "未登录用户无法评论"

        with allure.step("测试更新评论"):
            data = {"content": "Updated comment"}
            response = client.put(
                reverse("post:comment_detail", args=[comment.id]), data
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 401
            assert response.data["message"] == "未登录用户无法修改评论"

        with allure.step("测试删除评论"):
            response = client.delete(reverse("post:comment_detail", args=[comment.id]))
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 401
            assert response.data["message"] == "未登录用户无法删除评论"
