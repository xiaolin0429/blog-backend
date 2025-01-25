from django.contrib.auth import get_user_model
from django.utils import timezone

import factory
from faker import Faker

from apps.post.models import Comment, Post

fake = Faker(["zh_CN"])


class UserFactory(factory.django.DjangoModelFactory):
    """用户工厂类"""

    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class PostFactory(factory.django.DjangoModelFactory):
    """文章工厂类"""

    class Meta:
        model = Post

    title = factory.LazyFunction(lambda: fake.sentence())
    content = factory.LazyFunction(lambda: fake.text())
    author = factory.SubFactory(UserFactory)
    status = "published"
    published_at = factory.LazyFunction(timezone.now)


class CommentFactory(factory.django.DjangoModelFactory):
    """评论工厂类"""

    class Meta:
        model = Comment
        skip_postgeneration_save = True  # 避免在设置created_at后再次保存

    content = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    author = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)
    parent = None
    created_at = factory.LazyFunction(timezone.now)  # 默认使用当前时间

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """重写创建方法，确保created_at字段被正确设置"""
        obj = super()._create(model_class, *args, **kwargs)
        if "created_at" in kwargs:
            obj.created_at = kwargs["created_at"]
            obj.save()
        return obj
