import allure
from django.urls import reverse
from django.utils import timezone

import pytest
from rest_framework import status

from apps.post.models import Category, Post, Tag
from tests.apps.post.factories import PostFactory, UserFactory, CategoryFactory, TagFactory


@allure.epic("文章管理")
@allure.feature("文章列表")
@pytest.mark.django_db
class TestPostListView:
    @allure.story("匿名访问")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试匿名用户只能看到已发布的文章")
    @pytest.mark.high
    def test_get_post_list_as_anonymous(self, api_client):
        """测试匿名用户只能看到已发布的文章"""
        with allure.step("发送获取文章列表请求"):
            url = reverse("post:post_list")
            response = api_client.get(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["data"]["count"] == 0
            assert len(response.data["data"]["results"]) == 0

    @allure.story("普通用户访问")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试普通用户只能看到已发布的文章")
    @pytest.mark.high
    def test_get_post_list_as_normal_user(self, normal_user, api_client):
        """测试普通用户只能看到已发布的文章"""
        with allure.step("创建测试文章"):
            # 创建一篇已发布的文章
            Post.objects.create(
                title="已发布文章", content="内容", author=normal_user, status="published"
            )

            # 创建一篇草稿
            Post.objects.create(
                title="草稿文章", content="内容", author=normal_user, status="draft"
            )

        with allure.step("发送获取文章列表请求"):
            api_client.force_authenticate(user=normal_user)
            url = reverse("post:post_list")
            response = api_client.get(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["data"]["count"] == 1  # 总数为1
            assert len(response.data["data"]["results"]) == 1  # 结果列表长度为1
            assert response.data["data"]["results"][0]["title"] == "已发布文章"

    @allure.story("管理员访问")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试管理员可以看到所有文章")
    @pytest.mark.high
    def test_get_post_list_as_admin(self, admin_user, api_client):
        """测试管理员可以看到所有文章"""
        with allure.step("创建测试文章"):
            # 创建三篇不同状态的文章
            Post.objects.create(
                title="已发布文章", content="内容", author=admin_user, status="published"
            )
            Post.objects.create(
                title="草稿文章", content="内容", author=admin_user, status="draft"
            )
            Post.objects.create(
                title="已归档文章", content="内容", author=admin_user, status="archived"
            )

        with allure.step("发送获取文章列表请求"):
            api_client.force_authenticate(user=admin_user)
            url = reverse("post:post_list")
            response = api_client.get(url)

        with allure.step("验证响应结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["data"]["count"] == 3  # 总数为3
            assert len(response.data["data"]["results"]) == 3  # 结果列表长度为3

    @allure.story("分类筛选")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试按分类筛选文章的功能")
    @pytest.mark.medium
    def test_filter_posts_by_category(self, normal_user, api_client):
        """测试按分类筛选文章"""
        with allure.step("创建测试数据"):
            # 创建两个分类
            category1 = Category.objects.create(name="分类1")
            category2 = Category.objects.create(name="分类2")

            # 创建两篇文章,分别属于不同分类
            Post.objects.create(
                title="文章1",
                content="内容1",
                author=normal_user,
                category=category1,
                status="published",
            )
            Post.objects.create(
                title="文章2",
                content="内容2",
                author=normal_user,
                category=category2,
                status="published",
            )

        with allure.step("发送筛选请求"):
            api_client.force_authenticate(user=normal_user)
            url = reverse("post:post_list")
            response = api_client.get(f"{url}?category={category1.id}")

        with allure.step("验证筛选结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["data"]["count"] == 1  # 总数为1
            assert len(response.data["data"]["results"]) == 1  # 结果列表长度为1
            assert response.data["data"]["results"][0]["category"] == category1.id

    @allure.story("标签筛选")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试按标签筛选文章的功能")
    @pytest.mark.medium
    def test_filter_posts_by_tags(self, normal_user, api_client):
        """测试按标签筛选文章"""
        with allure.step("创建测试数据"):
            # 创建两个标签
            tag1 = Tag.objects.create(name="标签1")
            tag2 = Tag.objects.create(name="标签2")

            # 创建两篇文章,分别添加不同标签
            post1 = Post.objects.create(
                title="文章1", content="内容1", author=normal_user, status="published"
            )
            post1.tags.add(tag1)

            post2 = Post.objects.create(
                title="文章2", content="内容2", author=normal_user, status="published"
            )
            post2.tags.add(tag2)

        with allure.step("发送筛选请求"):
            api_client.force_authenticate(user=normal_user)
            url = reverse("post:post_list")
            response = api_client.get(f"{url}?tags={tag1.id}")

        with allure.step("验证筛选结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["data"]["count"] == 1  # 总数为1
            assert len(response.data["data"]["results"]) == 1  # 结果列表长度为1
            assert response.data["data"]["results"][0]["title"] == "文章1"

    @allure.story("文章搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试搜索文章的功能")
    @pytest.mark.medium
    def test_search_posts(self, normal_user, api_client):
        """测试搜索文章"""
        with allure.step("创建测试数据"):
            # 创建两篇包含Python的文章
            Post.objects.create(
                title="Python教程",
                content="Python入门指南",
                author=normal_user,
                status="published",
            )
            Post.objects.create(
                title="Django教程",
                content="Django入门指南",
                author=normal_user,
                status="published",
            )

        with allure.step("发送搜索请求"):
            api_client.force_authenticate(user=normal_user)
            url = reverse("post:post_list")
            response = api_client.get(f"{url}?search=Python")

        with allure.step("验证搜索结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["data"]["count"] == 1  # 总数为1
            assert len(response.data["data"]["results"]) == 1  # 结果列表长度为1
            assert "Python" in response.data["data"]["results"][0]["title"]

    @allure.story("文章排序")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试文章列表的排序功能")
    @pytest.mark.medium
    def test_order_posts(self, normal_user, api_client):
        """测试文章排序"""
        with allure.step("创建测试数据"):
            base_time = timezone.now()

            # 创建两篇文章，确保创建时间有间隔
            post1 = Post.objects.create(
                title="文章1",
                content="内容1",
                author=normal_user,
                views=10,
                likes=5,
                status="published",
                created_at=base_time - timezone.timedelta(hours=1),
            )
            post2 = Post.objects.create(
                title="文章2",
                content="内容2",
                author=normal_user,
                views=20,
                likes=15,
                status="published",
                created_at=base_time,
            )

        with allure.step("测试按浏览量排序"):
            api_client.force_authenticate(user=normal_user)
            url = reverse("post:post_list")
            response = api_client.get(f"{url}?ordering=-views")
            assert response.status_code == status.HTTP_200_OK
            assert response.data["data"]["results"][0]["title"] == "文章2"

        with allure.step("测试按点赞数排序"):
            response = api_client.get(f"{url}?ordering=-likes")
            assert response.status_code == status.HTTP_200_OK
            assert response.data["data"]["results"][0]["title"] == "文章2"

        with allure.step("测试按创建时间排序"):
            response = api_client.get(f"{url}?ordering=-created_at")
            assert response.status_code == status.HTTP_200_OK
            assert response.data["data"]["results"][0]["title"] == "文章2"
            assert response.data["data"]["results"][1]["title"] == "文章1"
