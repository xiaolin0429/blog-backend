import logging

from django.utils import timezone

from rest_framework import serializers

from apps.core.serializers import TimezoneSerializerMixin

from ..models import Post
from .category import CategorySerializer
from .comment import CommentSerializer
from .tag import TagSerializer

# 创建日志记录器
logger = logging.getLogger(__name__)


class PostListSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """文章列表序列化器"""

    author_username = serializers.CharField(source="author.username", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "excerpt",
            "author",
            "author_username",
            "category",
            "category_name",
            "tags",
            "status",
            "comments_count",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = ["author", "created_at", "updated_at", "published_at"]


class PostDetailSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """文章详情序列化器"""

    author_username = serializers.CharField(source="author.username", read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "excerpt",
            "author",
            "author_username",
            "category",
            "tags",
            "status",
            "comments",
            "cover",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = ["author", "created_at", "updated_at", "published_at"]

    def get_comments(self, obj):
        # 只获取顶级评论
        comments = obj.comments.filter(parent=None)
        return CommentSerializer(comments, many=True, context=self.context).data


class PostCreateUpdateSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """文章创建和更新序列化器"""

    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    category_id = serializers.IntegerField(source="category.id", required=False)
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    allowComment = serializers.BooleanField(source="allow_comment", required=False)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "excerpt",
            "category",
            "category_id",
            "tag_ids",
            "tags",
            "status",
            "pinned",
            "allow_comment",
            "allowComment",
            "published_at",
            "author",
            "author_username",
            "cover",
        ]
        read_only_fields = ["created_at", "updated_at", "author", "author_username"]
        extra_kwargs = {
            "excerpt": {"required": False},  # 摘要字段设为非必填
            "published_at": {"required": False},  # 发布时间设为非必填
            "pinned": {"required": False},  # 置顶字段设为非必填
            "allow_comment": {"required": False},  # 允许评论字段设为非必填
        }

    def validate(self, attrs):
        """验证数据"""
        logger.info(f"开始验证数据: {attrs}")
        try:
            validated_data = super().validate(attrs)
            logger.info(f"数据验证成功: {validated_data}")
            return validated_data
        except Exception as e:
            logger.error(f"数据验证失败: {str(e)}")
            raise

    def create(self, validated_data):
        """创建文章"""
        logger.info(f"开始创建文章，验证后的数据: {validated_data}")
        try:
            tag_ids = validated_data.pop("tag_ids", [])
            logger.info(f"处理标签: {tag_ids}")

            category_data = validated_data.pop("category", None)
            logger.info(f"处理分类: {category_data}")

            validated_data["author"] = self.context["request"].user
            logger.info(f"设置作者: {validated_data['author']}")

            if validated_data.get("status") == "published":
                validated_data["published_at"] = timezone.now()
                logger.info("文章状态为已发布，设置发布时间")

            # 处理分类
            if category_data and "id" in category_data:
                validated_data["category_id"] = category_data["id"]
                logger.info(f"设置分类ID: {category_data['id']}")

            logger.info(f"最终创建数据: {validated_data}")
            instance = super().create(validated_data)

            if tag_ids:
                instance.tags.set(tag_ids)
                logger.info(f"设置标签完成: {tag_ids}")

            logger.info(f"文章创建成功: ID={instance.id}")
            return instance
        except Exception as e:
            logger.error(f"创建文章失败: {str(e)}")
            raise

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop("tag_ids", None)
        category_data = validated_data.pop("category", None)

        # 处理分类
        if category_data and "id" in category_data:
            validated_data["category_id"] = category_data["id"]

        if (
            "status" in validated_data
            and validated_data["status"] == "published"
            and instance.status == "draft"
        ):
            validated_data["published_at"] = timezone.now()

        instance = super().update(instance, validated_data)
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        return instance


class PostAutoSaveSerializer(serializers.ModelSerializer):
    """文章自动保存序列化器"""

    class Meta:
        model = Post
        fields = ["title", "content", "excerpt", "category", "tags"]

    def update(self, instance, validated_data):
        # 保存当前版本到自动保存字段
        instance.auto_save_content = {
            "title": validated_data.get("title", instance.title),
            "content": validated_data.get("content", instance.content),
            "excerpt": validated_data.get("excerpt", instance.excerpt),
            "category": validated_data.get("category", instance.category).id
            if validated_data.get("category", instance.category)
            else None,
            "tags": list(instance.tags.values_list("id", flat=True)),
            "version": instance.version,
            "auto_save_time": timezone.now().isoformat(),
        }
        instance.save(update_fields=["auto_save_content"])
        return instance


class PostAutoSaveResponseSerializer(serializers.ModelSerializer):
    """文章自动保存响应序列化器"""

    auto_save_content = serializers.JSONField()

    class Meta:
        model = Post
        fields = ["auto_save_content"]

    def to_representation(self, instance):
        return instance.auto_save_content


class PostBriefSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """文章简要信息序列化器"""

    author_username = serializers.CharField(source="author.username", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "excerpt",
            "author_username",
            "category_name",
            "created_at",
        ]
        read_only_fields = fields
