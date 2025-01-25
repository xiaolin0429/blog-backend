#!/usr/bin/env python
import os
import sys
from pathlib import Path

import django

# 设置Django环境
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.urls import get_resolver
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions


def update_swagger_docs():
    """
    自动更新Swagger文档
    """
    print("开始更新API文档...")

    # 获取所有URL patterns
    resolver = get_resolver()

    # 创建新的schema view
    schema_view = get_schema_view(
        openapi.Info(
            title="Blog API",
            default_version="v1",
            description="Blog API documentation",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@blog.local"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    # 生成新的schema
    generator = OpenAPISchemaGenerator()
    schema = generator.get_schema(request=None, public=True)

    # 保存schema到文件
    output_file = Path(__file__).resolve().parent.parent / "static" / "swagger.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(schema.to_json())

    print(f"API文档已更新并保存到: {output_file}")

    # 打印API端点统计
    endpoints = set()
    for pattern in resolver.url_patterns:
        if hasattr(pattern, "callback") and hasattr(pattern.callback, "__name__"):
            endpoints.add(pattern.pattern)

    print(f"\n发现 {len(endpoints)} 个API端点:")
    for endpoint in sorted(endpoints):
        print(f"- {endpoint}")


if __name__ == "__main__":
    update_swagger_docs()
