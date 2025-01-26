from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import allure
import pytest
from rest_framework import status

from tests.apps.post.factories import PostFactory, UserFactory


@allure.epic("文章管理")
@allure.feature("文章搜索")
@pytest.mark.django_db
class TestSearchView:
    @allure.story("参数验证")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试搜索时未提供关键词的情况")
    @pytest.mark.medium
    def test_search_without_keyword(self, api_client):
        """测试没有关键词的搜索"""
        with allure.step("发送无关键词的搜索请求"):
            url = reverse("post:search")
            response = api_client.get(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert "搜索关键词不能为空" in response.data["message"]

    @allure.story("基础搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试基本的文章搜索功能")
    @pytest.mark.high
    def test_search_posts(self, api_client, user_factory, post_factory):
        """测试文章搜索"""
        with allure.step("准备测试数据"):
            user = user_factory()
            post_factory(
                title="Python教程",
                content="这是一篇Python教程",
                excerpt="Python入门指南",
                author=user,
                status="published",
            )
            post_factory(
                title="Django教程",
                content="这是一篇Django教程",
                excerpt="Django入门指南",
                author=user,
                status="published",
            )

        with allure.step("发送搜索请求"):
            url = reverse("post:search")
            response = api_client.get(f"{url}?keyword=Python")

        with allure.step("验证搜索结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["count"] == 1
            assert "Python" in response.data["data"]["results"][0]["title"]

    @allure.story("搜索过滤")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试带过滤条件的文章搜索功能")
    @pytest.mark.medium
    def test_search_with_filters(self, api_client, user_factory, post_factory):
        """测试带过滤条件的搜索"""
        with allure.step("准备测试数据"):
            user = user_factory()
            post = post_factory(
                title="Python教程",
                content="这是一篇Python教程",
                excerpt="Python入门指南",
                author=user,
                status="published",
            )

        with allure.step("发送带过滤条件的搜索请求"):
            url = reverse("post:search")
            response = api_client.get(f"{url}?keyword=Python&highlight=false")  # 禁用高亮

        with allure.step("验证搜索结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["count"] == 1
            assert response.data["data"]["results"][0]["title"] == "Python教程"

    @allure.story("日期搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试按日期范围搜索文章")
    @pytest.mark.medium
    def test_search_with_date_range(self, api_client, user_factory, post_factory):
        """测试日期范围搜索"""
        with allure.step("准备测试数据"):
            user = user_factory()
            current_date = timezone.now()
            post_factory(
                title="Python教程",
                content="这是一篇Python教程",
                author=user,
                status="published",
                created_at=current_date,
            )

            # 使用前后一天的范围，避免时区问题
            start_date = (current_date - timedelta(days=1)).date().isoformat()
            end_date = (current_date + timedelta(days=1)).date().isoformat()

        with allure.step("发送日期范围搜索请求"):
            url = reverse("post:search")
            response = api_client.get(
                f"{url}?keyword=Python&date_start={start_date}&date_end={end_date}"
            )

        with allure.step("验证搜索结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert response.data["data"]["count"] == 1

    @allure.story("搜索高亮")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试搜索结果的关键词高亮功能")
    @pytest.mark.medium
    def test_search_with_highlight(self, api_client, user_factory, post_factory):
        """测试搜索结果高亮"""
        with allure.step("准备测试数据"):
            user = user_factory()
            post_factory(
                title="Python教程", 
                content="这是一篇Python教程", 
                author=user, 
                status="published"
            )

        with allure.step("发送带高亮的搜索请求"):
            url = reverse("post:search")
            response = api_client.get(f"{url}?keyword=Python&highlight=true")

        with allure.step("验证高亮结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert (
                '<span class="search-highlight">Python</span>'
                in response.data["data"]["results"][0]["title"]
            )


@allure.epic("文章管理")
@allure.feature("搜索建议")
@pytest.mark.django_db
class TestSearchSuggestView:
    @allure.story("参数验证")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试搜索建议时未提供关键词的情况")
    @pytest.mark.medium
    def test_suggest_without_keyword(self, api_client):
        """测试没有关键词的搜索建议"""
        with allure.step("发送无关键词的建议请求"):
            url = reverse("post:search_suggest")
            response = api_client.get(url)

        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 400
            assert "搜索关键词不能为空" in response.data["message"]

    @allure.story("文章建议")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试文章相关的搜索建议功能")
    @pytest.mark.high
    def test_suggest_posts(self, api_client, user_factory, post_factory):
        """测试文章搜索建议"""
        with allure.step("准备测试数据"):
            user = user_factory()
            post_factory(
                title="Python教程",
                content="这是一篇Python教程",
                excerpt="Python入门指南",
                author=user,
                status="published",
            )

        with allure.step("发送搜索建议请求"):
            url = reverse("post:search_suggest")
            response = api_client.get(f"{url}?keyword=Python")

        with allure.step("验证建议结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert len(response.data["data"]["suggestions"]) > 0
            assert response.data["data"]["suggestions"][0]["type"] == "post"
            assert "Python" in response.data["data"]["suggestions"][0]["title"]

    @allure.story("分类和标签建议")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试分类和标签的搜索建议功能")
    @pytest.mark.medium
    def test_suggest_categories_and_tags(self, api_client, post_factory):
        """测试分类和标签搜索建议"""
        with allure.step("准备测试数据"):
            post = post_factory(title="Python教程", status="published")
            # 工厂会自动创建关联的分类和标签

        with allure.step("发送搜索建议请求"):
            url = reverse("post:search_suggest")
            response = api_client.get(f"{url}?keyword=Python")

        with allure.step("验证建议结果"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            suggestions = response.data["data"]["suggestions"]
            # 验证返回的建议中包含文章、分类或标签
            assert any(s["type"] in ["post", "category", "tag"] for s in suggestions)

    @allure.story("建议数量限制")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试搜索建议的数量限制功能")
    @pytest.mark.medium
    def test_suggest_limit(self, api_client, user_factory, post_factory):
        """测试搜索建议数量限制"""
        with allure.step("准备测试数据"):
            user = user_factory()
            for i in range(15):
                post_factory(
                    title=f"Python教程{i}",
                    content=f"这是一篇Python教程{i}",
                    author=user,
                    status="published",
                )

        with allure.step("发送带数量限制的搜索建议请求"):
            url = reverse("post:search_suggest")
            response = api_client.get(f"{url}?keyword=Python&limit=5")

        with allure.step("验证建议数量"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert len(response.data["data"]["suggestions"]) == 5
