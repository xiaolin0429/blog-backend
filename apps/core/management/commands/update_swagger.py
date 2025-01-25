import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import URLPattern, URLResolver, get_resolver

from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


class Command(BaseCommand):
    help = "更新Swagger API文档"

    def collect_urls(self, patterns, prefix=""):
        """递归收集所有URL模式"""
        urls = []
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                # 只收集API相关的URL
                full_path = prefix + str(pattern.pattern)
                if "api/v1" in full_path and not any(
                    x in full_path for x in ["swagger", "redoc"]
                ):
                    urls.append(full_path)
            elif isinstance(pattern, URLResolver):
                new_prefix = prefix + str(pattern.pattern)
                urls.extend(self.collect_urls(pattern.url_patterns, new_prefix))
        return urls

    def handle(self, *args, **options):
        self.stdout.write("开始更新API文档...")

        # 获取所有URL patterns
        resolver = get_resolver()

        # 创建API信息
        info = openapi.Info(
            title="个人博客系统API文档",
            default_version="v1",
            description="个人博客系统API接口文档",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@blog.local"),
            license=openapi.License(name="BSD License"),
        )

        # 创建schema生成器
        generator = OpenAPISchemaGenerator(info=info, patterns=resolver.url_patterns)

        # 创建一个假的请求对象
        factory = APIRequestFactory()
        wsgi_request = factory.get("/swagger.json", HTTP_HOST=settings.ALLOWED_HOSTS[0])
        request = Request(wsgi_request)

        # 生成schema
        schema = generator.get_schema(request=request, public=True)

        # 保存schema到文件
        output_file = (
            Path(__file__).resolve().parent.parent.parent.parent.parent
            / "static"
            / "swagger.json"
        )
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(schema.as_odict(), f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"API文档已更新并保存到: {output_file}"))

        # 打印API端点统计
        endpoints = self.collect_urls(resolver.url_patterns, prefix="")

        self.stdout.write(f"\n发现 {len(endpoints)} 个API端点:")
        for endpoint in sorted(endpoints):
            self.stdout.write(f"- {endpoint}")
