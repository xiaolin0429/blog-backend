from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import allure
import pytest
from rest_framework import status

from apps.post.models import Comment, Post
from tests.apps.post.factories import PostFactory, UserFactory, CommentFactory


@allure.epic("评论管理")
@allure.feature("全局评论")
@pytest.mark.django_db
class TestGlobalCommentAPI:
    """全局评论API测试"""

    @allure.story("评论列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试匿名用户获取全局评论列表")
    @pytest.mark.medium
    def test_list_comments_anonymous(self, client, comment):
        with allure.step("获取评论列表"):
            response = client.get(reverse("post:global_comment_list"))
            
        with allure.step("验证响应"):
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert isinstance(response.data["data"], dict)
            assert "results" in response.data["data"]
            assert "count" in response.data["data"]
            assert isinstance(response.data["data"]["results"], list)

    @allure.story("评论列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试评论列表分页功能")
    @pytest.mark.high
    def test_list_comments_pagination(self, auth_client, post, user):
        with allure.step("创建测试评论"):
            for i in range(15):
                Comment.objects.create(
                    content=f"Comment {i}", post=post, author=user
                )

        with allure.step("测试第一页"):
            response = auth_client.get(
                reverse("post:global_comment_list"), {"page": 1, "page_size": 10}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert len(response.data["data"]["results"]) == 10
            assert response.data["data"]["count"] == 15

        with allure.step("测试第二页"):
            response = auth_client.get(
                reverse("post:global_comment_list"), {"page": 2, "page_size": 10}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            assert len(response.data["data"]["results"]) == 5
            assert response.data["data"]["count"] == 15

    @allure.story("评论列表")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试评论列表排序功能")
    @pytest.mark.medium
    def test_list_comments_ordering(self, auth_client, post, user):
        with allure.step("创建不同时间的评论"):
            base_time = timezone.now()
            for i in range(5):
                Comment.objects.create(
                    content=f"Comment {i}",
                    post=post,
                    author=user,
                    created_at=base_time - timedelta(days=i, hours=i),
                )

        with allure.step("测试按创建时间降序排序"):
            response = auth_client.get(
                reverse("post:global_comment_list"), {"ordering": "-created_at"}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            results = response.data["data"]["results"]
            assert len(results) == 5
            for i in range(len(results) - 1):
                assert results[i]["created_at"] > results[i + 1]["created_at"]

        with allure.step("测试按创建时间升序排序"):
            response = auth_client.get(
                reverse("post:global_comment_list"), {"ordering": "created_at"}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            results = response.data["data"]["results"]
            assert len(results) == 5
            for i in range(len(results) - 1):
                assert results[i]["created_at"] < results[i + 1]["created_at"]

    @allure.story("评论过滤")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试按文章过滤评论")
    @pytest.mark.medium
    def test_filter_by_post(self, auth_client, post, other_post, user):
        with allure.step("创建不同文章的评论"):
            comment1 = Comment.objects.create(
                content="Comment on first post", post=post, author=user
            )
            comment2 = Comment.objects.create(
                content="Comment on second post", post=other_post, author=user
            )

        with allure.step("测试按文章过滤"):
            response = auth_client.get(
                reverse("post:global_comment_list"), {"post": post.id}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            results = response.data["data"]["results"]
            assert len(results) == 1
            assert results[0]["post"] == post.id

    @allure.story("评论过滤")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试按作者过滤评论")
    @pytest.mark.medium
    def test_filter_by_author(self, auth_client, post, user, other_user):
        with allure.step("创建不同作者的评论"):
            comment1 = Comment.objects.create(
                content="Comment by first user", post=post, author=user
            )
            comment2 = Comment.objects.create(
                content="Comment by second user", post=post, author=other_user
            )

        with allure.step("测试按作者过滤"):
            response = auth_client.get(
                reverse("post:global_comment_list"), {"author": user.id}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            results = response.data["data"]["results"]
            assert len(results) == 1
            assert results[0]["author"]["id"] == user.id

    @allure.story("评论过滤")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试按日期范围过滤评论")
    @pytest.mark.medium
    def test_filter_by_date_range(self, auth_client, post, user):
        with allure.step("创建不同日期的评论"):
            base_time = timezone.now()
            dates = [
                base_time - timedelta(days=5),
                base_time - timedelta(days=3),
                base_time - timedelta(days=1),
            ]

            for i, date in enumerate(dates):
                Comment.objects.create(
                    content=f'Comment on {date.strftime("%Y-%m-%d")}',
                    post=post,
                    author=user,
                    created_at=date,
                )

        with allure.step("测试按日期范围过滤"):
            start_date = (base_time - timedelta(days=3)).date()
            end_date = base_time.date()

            response = auth_client.get(
                reverse("post:global_comment_list"),
                {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            )

            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            results = response.data["data"]["results"]
            assert len(results) == 2

    @allure.story("评论搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试按关键词搜索评论")
    @pytest.mark.medium
    def test_search_by_keyword(self, auth_client, post, user):
        with allure.step("创建测试评论"):
            Comment.objects.create(content="This is a test comment", post=post, author=user)
            Comment.objects.create(
                content="Another regular comment", post=post, author=user
            )
            Comment.objects.create(content="Nothing special here", post=post, author=user)

        with allure.step("测试关键词搜索"):
            response = auth_client.get(
                reverse("post:global_comment_list"), {"keyword": "test"}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            results = response.data["data"]["results"]
            assert len(results) == 3
            assert any("test" in result["content"].lower() for result in results)

    @allure.story("评论排序")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试按创建时间排序评论")
    @pytest.mark.medium
    def test_order_comments_by_created_at(self, auth_client, post, user):
        with allure.step("创建不同时间的评论"):
            base_time = timezone.now()
            dates = [
                base_time - timedelta(days=2, hours=2),
                base_time - timedelta(days=1, hours=1),
                base_time,
            ]
            for i, date in enumerate(dates):
                Comment.objects.create(
                    content=f"Comment {i}", post=post, author=user, created_at=date
                )

        with allure.step("测试按创建时间升序排序"):
            response = auth_client.get(
                reverse("post:global_comment_list"), {"ordering": "created_at"}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            results = response.data["data"]["results"]
            assert len(results) == 3
            for i in range(len(results) - 1):
                assert results[i]["created_at"] < results[i + 1]["created_at"]

        with allure.step("测试按创建时间降序排序"):
            response = auth_client.get(
                reverse("post:global_comment_list"), {"ordering": "-created_at"}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            results = response.data["data"]["results"]
            assert len(results) == 3
            for i in range(len(results) - 1):
                assert results[i]["created_at"] > results[i + 1]["created_at"]

    @allure.story("评论排序")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试按回复数量排序评论")
    @pytest.mark.medium
    def test_order_comments_by_reply_count(self, auth_client, post, user):
        with allure.step("创建主评论"):
            main_comment1 = Comment.objects.create(
                content="Main comment 1", post=post, author=user
            )
            main_comment2 = Comment.objects.create(
                content="Main comment 2", post=post, author=user
            )

        with allure.step("创建回复评论"):
            Comment.objects.create(
                content="Reply 1", post=post, author=user, parent=main_comment1
            )
            Comment.objects.create(
                content="Reply 2", post=post, author=user, parent=main_comment1
            )
            Comment.objects.create(
                content="Reply 3", post=post, author=user, parent=main_comment2
            )

        with allure.step("测试按回复数量排序"):
            response = auth_client.get(
                reverse("post:global_comment_list"), {"ordering": "-reply_count"}
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.data["code"] == 200
            results = response.data["data"]["results"]
            assert len(results) == 2  # Only main comments
            assert results[0]["reply_count"] == 2  # main_comment1
            assert results[1]["reply_count"] == 1  # main_comment2
