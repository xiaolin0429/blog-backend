from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器"""

    status = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "nickname",
            "status",
            "role",
            "last_login",
            "date_joined",
        ]

    def get_status(self, obj):
        return "active" if obj.is_active else "inactive"

    def get_role(self, obj):
        if obj.is_superuser:
            return "superadmin"
        elif obj.is_staff:
            return "admin"
        return "user"


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""

    status = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "nickname",
            "bio",
            "status",
            "role",
            "avatar",
            "last_login",
            "date_joined",
            "is_active",
            "is_staff",
        ]

    def get_status(self, obj):
        return "active" if obj.is_active else "inactive"

    def get_role(self, obj):
        if obj.is_superuser:
            return "superadmin"
        elif obj.is_staff:
            return "admin"
        return "user"


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "nickname", "is_active", "is_staff"]

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

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "nickname",
            "bio",
            "is_active",
            "is_staff",
            "is_superuser",
            "avatar",
        ]
        read_only_fields = ["username"]  # 用户名不允许修改

    def validate_email(self, value):
        """验证邮箱唯一性"""
        instance = self.instance
        if User.objects.exclude(pk=instance.pk).filter(email=value).exists():
            raise serializers.ValidationError("邮箱已被注册")
        return value
