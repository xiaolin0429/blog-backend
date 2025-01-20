from rest_framework import serializers
from django.utils import timezone
from apps.core.serializers import TimezoneSerializerMixin
from ..models import Post
from .category import CategorySerializer
from .tag import TagSerializer
from .comment import CommentSerializer

class PostListSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """文章列表序列化器"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'excerpt', 'author', 'author_username', 'category',
                 'category_name', 'tags', 'status', 'comments_count', 'created_at',
                 'updated_at', 'published_at']
        read_only_fields = ['author', 'created_at', 'updated_at', 'published_at']

class PostDetailSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """文章详情序列化器"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'excerpt', 'author', 'author_username',
                 'category', 'tags', 'status', 'comments', 'created_at', 'updated_at',
                 'published_at']
        read_only_fields = ['author', 'created_at', 'updated_at', 'published_at']

    def get_comments(self, obj):
        # 只获取顶级评论
        comments = obj.comments.filter(parent=None)
        return CommentSerializer(comments, many=True, context=self.context).data

class PostCreateUpdateSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """文章创建和更新序列化器"""
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'excerpt', 'category', 'tags', 
                 'status', 'published_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'category': {'required': False},  # 分类字段设为非必填
            'tags': {'required': False},      # 标签字段设为非必填
            'excerpt': {'required': False},   # 摘要字段设为非必填
            'published_at': {'required': False}  # 发布时间设为非必填
        }

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        if validated_data.get('status') == 'published':
            validated_data['published_at'] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if ('status' in validated_data and
            validated_data['status'] == 'published' and
            instance.status == 'draft'):
            validated_data['published_at'] = timezone.now()
        return super().update(instance, validated_data) 