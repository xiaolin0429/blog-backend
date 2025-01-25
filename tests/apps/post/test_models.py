from django.utils import timezone

import pytest

from apps.post.models import Post


@pytest.mark.django_db
class TestPostModel:
    def test_create_post(self, normal_user):
        """测试创建文章"""
        post = Post.objects.create(
            title="测试文章",
            content="这是测试内容",
            excerpt="这是摘要",
            author=normal_user,
        )
        assert post.title == "测试文章"
        assert post.content == "这是测试内容"
        assert post.excerpt == "这是摘要"
        assert post.author == normal_user
        assert post.status == "draft"  # 默认状态为草稿
        assert post.views == 0  # 默认浏览量为0
        assert post.likes == 0  # 默认点赞数为0
        assert not post.is_deleted  # 默认未删除
        assert post.published_at is None  # 未发布时发布时间为空
        assert post.deleted_at is None  # 未删除时删除时间为空

    def test_post_str_representation(self, normal_user):
        """测试文章的字符串表示"""
        post = Post.objects.create(
            title="测试文章",
            content="这是测试内容",
            author=normal_user,
        )
        assert str(post) == "测试文章"

    def test_post_publish(self, normal_user):
        """测试发布文章时的状态和时间处理"""
        post = Post.objects.create(
            title="测试文章",
            content="这是测试内容",
            author=normal_user,
        )
        assert post.status == "draft"
        assert post.published_at is None

        # 发布文章
        post.status = "published"
        post.save()
        assert post.status == "published"
        assert post.published_at is not None
        assert isinstance(post.published_at, timezone.datetime)

    def test_post_soft_delete(self, normal_user):
        """测试文章的软删除功能"""
        post = Post.objects.create(
            title="测试文章",
            content="这是测试内容",
            author=normal_user,
        )
        assert not post.is_deleted
        assert post.deleted_at is None

        # 软删除文章
        post.soft_delete()
        assert post.is_deleted
        assert post.deleted_at is not None
        assert isinstance(post.deleted_at, timezone.datetime)

    def test_post_restore(self, normal_user):
        """测试恢复已删除的文章"""
        post = Post.objects.create(
            title="测试文章",
            content="这是测试内容",
            author=normal_user,
        )
        post.soft_delete()
        assert post.is_deleted
        assert post.deleted_at is not None

        # 恢复文章
        post.restore()
        assert not post.is_deleted
        assert post.deleted_at is None
        assert post.status == "draft"  # 恢复后状态应为草稿

    def test_post_ordering(self, normal_user):
        """测试文章的排序功能"""
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
            title="文章3", content="内容3", author=normal_user, created_at=base_time
        )

        # 获取所有文章，应该按创建时间倒序排列
        posts = Post.objects.all()
        assert posts[0] == post3  # 最新创建的文章应该在最前面
        assert posts[1] == post2
        assert posts[2] == post1
