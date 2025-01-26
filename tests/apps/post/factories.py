from django.contrib.auth import get_user_model
from django.utils import timezone

import factory
from faker import Faker

from apps.post.models import Comment, Post, Category, Tag

fake = Faker(["zh_CN"])


class UserFactory(factory.django.DjangoModelFactory):
    """用户工厂类"""

    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class CategoryFactory(factory.django.DjangoModelFactory):
    """分类工厂类"""

    class Meta:
        model = Category
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"分类{n}")
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    parent = None
    order = factory.Sequence(lambda n: n)


class TagFactory(factory.django.DjangoModelFactory):
    """标签工厂类"""

    class Meta:
        model = Tag
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"标签{n}")
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))


class PostFactory(factory.django.DjangoModelFactory):
    """文章工厂类"""

    class Meta:
        model = Post

    title = factory.LazyFunction(lambda: fake.sentence())
    content = factory.LazyFunction(lambda: fake.text())
    excerpt = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    status = "published"
    published_at = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        else:
            # 默认创建2个标签
            self.tags.add(TagFactory(), TagFactory())


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
