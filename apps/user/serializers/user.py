from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import serializers

from apps.core.serializers import TimezoneSerializerMixin

User = get_user_model()


class UserRegisterSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """用户注册序列化器"""

    username = serializers.CharField(
        required=True,
        min_length=4,
        max_length=20,
        validators=[
            RegexValidator(regex=r"^[a-zA-Z0-9_]+$", message="用户名只能包含字母、数字、下划线")
        ],
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        max_length=20,
        validators=[validate_password],
    )
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
    nickname = serializers.CharField(
        required=False, min_length=2, max_length=20, allow_null=True
    )

    class Meta:
        model = User
        fields = ("username", "password", "password2", "email", "nickname")

    def validate_username(self, value):
        """验证用户名唯一性"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_email(self, value):
        """验证邮箱唯一性"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被注册")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "两次密码不一致"})

        # 验证密码复杂度
        password = attrs["password"]
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError({"password": "密码必须包含数字"})
        if not any(char.isalpha() for char in password):
            raise serializers.ValidationError({"password": "密码必须包含字母"})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """用户个人信息序列化器"""

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "nickname",
            "avatar",
            "bio",
            "date_joined",
            "last_login",
        )
        read_only_fields = ("id", "username", "email", "date_joined", "last_login")

    def get_avatar(self, obj):
        """获取头像URL，如果没有则返回默认头像"""
        if obj.avatar and hasattr(obj.avatar, "url"):
            return obj.avatar.url
        return settings.DEFAULT_AVATAR_URL


class UserProfileUpdateSerializer(TimezoneSerializerMixin, serializers.ModelSerializer):
    """用户个人信息更新序列化器"""

    nickname = serializers.CharField(
        required=False, min_length=2, max_length=20, allow_null=True
    )
    avatar = serializers.ImageField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, max_length=500, allow_null=True)

    class Meta:
        model = User
        fields = ("nickname", "avatar", "bio")
