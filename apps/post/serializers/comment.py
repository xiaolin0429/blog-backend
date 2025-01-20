from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Comment

User = get_user_model()

class CommentUserSerializer(serializers.ModelSerializer):
    """评论用户信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'avatar']
        read_only_fields = fields

class CommentReplySerializer(serializers.ModelSerializer):
    """评论回复序列化器"""
    author = CommentUserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    author = CommentUserSerializer(read_only=True)
    replies = CommentReplySerializer(many=True, read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'parent', 'replies', 
                 'reply_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'replies', 'reply_count', 
                           'created_at', 'updated_at']
        
    def validate_parent(self, value):
        """验证父评论"""
        if value and value.parent:
            raise serializers.ValidationError("不能回复回复")
        return value
    
    def validate(self, attrs):
        """验证评论数据"""
        # 如果是回复，确保回复的是同一篇文章的评论
        parent = attrs.get('parent')
        if parent and parent.post != attrs['post']:
            raise serializers.ValidationError({"parent": "不能回复其他文章的评论"})
        return attrs
        
    def create(self, validated_data):
        """创建评论"""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data) 