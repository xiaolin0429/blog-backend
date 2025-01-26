from django.urls import reverse

import allure
import pytest
from rest_framework import status

from apps.post.models import Post
from tests.apps.post.factories import PostFactory, UserFactory


@allure.epic("文章管理")
@allure.feature("回收站")
@pytest.mark.django_db
class TestPostTrash:
    @allure.story("回收站列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试获取回收站中的文章列表")
    @pytest.mark.high
    def test_list_trash_posts(self, auth_client, user):
        """测试获取回收站文章列表"""
        with allure.step("创建测试数据"):
            Post.objects.create(title="已删除文章1", content="内容1", author=user, is_deleted=True)
            Post.objects.create(title="已删除文章2", content="内容2", author=user, is_deleted=True)

        with allure.step("获取回收站列表"):
            url = reverse("post:post_trash_list")
            response = auth_client.get(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert len(response.data["data"]["results"]) == 2
            assert response.data["data"]["count"] == 2

    @allure.story("回收站列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试获取空的回收站列表")
    @pytest.mark.medium
    def test_list_trash_posts_empty(self, auth_client):
        """测试获取空的回收站列表"""
        with allure.step("获取回收站列表"):
            url = reverse("post:post_trash_list")
            response = auth_client.get(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert len(response.data["data"]["results"]) == 0
            assert response.data["data"]["count"] == 0

    @allure.story("恢复文章")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试从回收站恢复文章")
    @pytest.mark.high
    def test_restore_post(self, auth_client, user):
        """测试恢复已删除的文章"""
        with allure.step("创建测试数据"):
            post = Post.objects.create(
                title="已删除文章", content="内容", author=user, is_deleted=True
            )

        with allure.step("恢复文章"):
            url = reverse("post:post_restore", kwargs={"pk": post.id})
            response = auth_client.post(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["status"] == "draft"
            assert response.data["data"]["id"] == post.id
            assert response.data["data"]["title"] == post.title
            
        with allure.step("验证数据库状态"):
            post.refresh_from_db()
            assert not post.is_deleted
            assert post.status == "draft"

    @allure.story("恢复文章")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试恢复不存在的文章")
    @pytest.mark.medium
    def test_restore_nonexistent_post(self, auth_client):
        """测试恢复不存在的文章"""
        with allure.step("尝试恢复不存在的文章"):
            url = reverse("post:post_restore", kwargs={"pk": 99999})
            response = auth_client.post(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert response.data["message"] == "文章不存在或无权限操作"

    @allure.story("永久删除")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试永久删除回收站中的文章")
    @pytest.mark.high
    def test_permanent_delete_post(self, auth_client, user):
        """测试永久删除文章"""
        with allure.step("创建测试数据"):
            post = Post.objects.create(
                title="已删除文章", content="内容", author=user, is_deleted=True
            )

        with allure.step("永久删除文章"):
            url = reverse("post:post_permanent_delete", kwargs={"pk": post.id})
            response = auth_client.delete(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 204
            assert response.data["message"] == "success"
            assert response.data["data"] is None
            
        with allure.step("验证数据库状态"):
            assert not Post.objects.filter(id=post.id).exists()

    @allure.story("永久删除")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试永久删除不存在的文章")
    @pytest.mark.medium
    def test_permanent_delete_nonexistent_post(self, auth_client):
        """测试永久删除不存在的文章"""
        with allure.step("尝试删除不存在的文章"):
            url = reverse("post:post_permanent_delete", kwargs={"pk": 99999})
            response = auth_client.delete(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 404
            assert response.data["message"] == "文章不存在或无权限操作"

    @allure.story("清空回收站")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试清空回收站功能")
    @pytest.mark.high
    def test_empty_trash(self, auth_client, user):
        """测试清空回收站"""
        with allure.step("创建测试数据"):
            Post.objects.create(title="已删除文章1", content="内容1", author=user, is_deleted=True)
            Post.objects.create(title="已删除文章2", content="内容2", author=user, is_deleted=True)

        with allure.step("清空回收站"):
            url = reverse("post:post_empty_trash")
            response = auth_client.delete(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 204
            assert response.data["message"] == "success"
            assert response.data["data"]["deleted_count"] == 2
            
        with allure.step("验证数据库状态"):
            assert not Post.objects.filter(is_deleted=True).exists()

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试未认证用户清空回收站")
    @pytest.mark.security
    def test_empty_trash_unauthenticated(self, client):
        """测试未认证用户清空回收站"""
        with allure.step("尝试清空回收站"):
            url = reverse("post:post_empty_trash")
            response = client.delete(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @allure.story("回收站列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试回收站文章列表分页功能")
    @pytest.mark.medium
    def test_list_trash_posts_pagination(self, auth_client, user):
        """测试回收站文章列表分页"""
        with allure.step("创建测试数据"):
            for i in range(11):
                Post.objects.create(
                    title=f"已删除文章{i}", 
                    content=f"内容{i}", 
                    author=user, 
                    is_deleted=True
                )

        with allure.step("获取第一页"):
            url = reverse("post:post_trash_list")
            response = auth_client.get(f"{url}?page=1&size=10")

            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert len(response.data["data"]["results"]) == 10
            assert response.data["data"]["count"] == 11

        with allure.step("获取第二页"):
            response = auth_client.get(f"{url}?page=2&size=10")
            assert response.status_code == status.HTTP_200_OK
            assert len(response.data["data"]["results"]) == 1

    @allure.story("权限控制")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试管理员查看所有用户的回收站文章")
    @pytest.mark.security
    def test_list_trash_posts_admin(self, auth_client, user, user_factory):
        """测试管理员查看所有用户的回收站文章"""
        with allure.step("创建测试数据"):
            normal_user = user_factory()
            admin_user = user_factory(is_staff=True)
            auth_client.force_authenticate(user=admin_user)

            Post.objects.create(title="用户1文章", content="内容1", author=normal_user, is_deleted=True)
            Post.objects.create(title="用户2文章", content="内容2", author=user, is_deleted=True)

        with allure.step("获取回收站列表"):
            url = reverse("post:post_trash_list")
            response = auth_client.get(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["count"] == 2  # 管理员可以看到所有用户的文章
