from django.utils import timezone

import allure
import pytest

from apps.post.models import Post
from tests.apps.post.factories import PostFactory, UserFactory


@allure.epic("文章管理")
@allure.feature("文章模型")
@pytest.mark.django_db
class TestPostModel:
    @allure.story("文章创建")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试创建文章时各个字段的默认值和基本属性")
    @pytest.mark.high
    def test_create_post(self, normal_user):
        """测试创建文章"""
        with allure.step("创建文章"):
            post = Post.objects.create(
                title="测试文章",
                content="这是测试内容",
                excerpt="这是摘要",
                author=normal_user,
            )
        
        with allure.step("验证文章基本属性"):
            assert post.title == "测试文章"
            assert post.content == "这是测试内容"
            assert post.excerpt == "这是摘要"
            assert post.author == normal_user
        
        with allure.step("验证文章默认值"):
            assert post.status == "draft"  # 默认状态为草稿
            assert post.views == 0  # 默认浏览量为0
            assert post.likes == 0  # 默认点赞数为0
            assert not post.is_deleted  # 默认未删除
            assert post.published_at is None  # 未发布时发布时间为空
            assert post.deleted_at is None  # 未删除时删除时间为空

    @allure.story("文章基础功能")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试文章的字符串表示方法")
    @pytest.mark.medium
    def test_post_str_representation(self, normal_user):
        """测试文章的字符串表示"""
        with allure.step("创建文章"):
            post = Post.objects.create(
                title="测试文章",
                content="这是测试内容",
                author=normal_user,
            )
        
        with allure.step("验证字符串表示"):
            assert str(post) == "测试文章"

    @allure.story("文章状态")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试发布文章时的状态变更和发布时间处理")
    @pytest.mark.high
    def test_post_publish(self, normal_user):
        """测试发布文章时的状态和时间处理"""
        with allure.step("创建草稿文章"):
            post = Post.objects.create(
                title="测试文章",
                content="这是测试内容",
                author=normal_user,
            )
            assert post.status == "draft"
            assert post.published_at is None

        with allure.step("发布文章"):
            post.status = "published"
            post.save()
        
        with allure.step("验证发布状态"):
            assert post.status == "published"
            assert post.published_at is not None
            assert isinstance(post.published_at, timezone.datetime)

    @allure.story("文章删除")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试文章的软删除功能")
    @pytest.mark.high
    def test_post_soft_delete(self, normal_user):
        """测试文章的软删除功能"""
        with allure.step("创建文章"):
            post = Post.objects.create(
                title="测试文章",
                content="这是测试内容",
                author=normal_user,
            )
            assert not post.is_deleted
            assert post.deleted_at is None

        with allure.step("软删除文章"):
            post.soft_delete()
        
        with allure.step("验证删除状态"):
            assert post.is_deleted
            assert post.deleted_at is not None
            assert isinstance(post.deleted_at, timezone.datetime)

    @allure.story("文章恢复")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试恢复已删除文章的功能")
    @pytest.mark.high
    def test_post_restore(self, normal_user):
        """测试恢复已删除的文章"""
        with allure.step("创建并删除文章"):
            post = Post.objects.create(
                title="测试文章",
                content="这是测试内容",
                author=normal_user,
            )
            post.soft_delete()
            assert post.is_deleted
            assert post.deleted_at is not None

        with allure.step("恢复文章"):
            post.restore()
        
        with allure.step("验证恢复状态"):
            assert not post.is_deleted
            assert post.deleted_at is None
            assert post.status == "draft"  # 恢复后状态应为草稿

    @allure.story("文章排序")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试文章的默认排序功能")
    @pytest.mark.medium
    def test_post_ordering(self, normal_user):
        """测试文章的排序功能"""
        with allure.step("准备测试数据"):
            base_time = timezone.now()

            # 创建三篇文章，每篇文章的创建时间间隔1小时
            post1 = Post.objects.create(
                title="文章1",
                content="内容1",
                author=normal_user,
                created_at=base_time - timezone.timedelta(hours=2),
            )
            post2 = Post.objects.create(
                title="文章2",
                content="内容2",
                author=normal_user,
                created_at=base_time - timezone.timedelta(hours=1),
            )
            post3 = Post.objects.create(
                title="文章3", 
                content="内容3", 
                author=normal_user, 
                created_at=base_time
            )

        with allure.step("验证排序结果"):
            # 获取所有文章，应该按创建时间倒序排列
            posts = Post.objects.all()
            assert posts[0] == post3  # 最新创建的文章应该在最前面
            assert posts[1] == post2
            assert posts[2] == post1
