import logging

from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .services import SystemService

logger = logging.getLogger(__name__)

# Create your views here.


@api_view(["GET"])
@permission_classes([IsAdminUser])
def system_overview(request):
    """获取系统概览信息"""
    try:
        logger.info("开始获取系统概览信息")

        logger.debug("获取系统信息...")
        system_info = SystemService.get_system_info()
        if "error" in system_info:
            raise Exception(system_info["error"])

        logger.debug("获取内容统计...")
        content_stats = SystemService.get_content_stats()
        if "error" in content_stats:
            raise Exception(content_stats["error"])

        logger.debug("获取存储统计...")
        storage_stats = SystemService.get_storage_stats()
        if "error" in storage_stats:
            raise Exception(storage_stats["error"])

        logger.debug("获取最近活动...")
        recent_activities = SystemService.get_recent_activities()
        if "error" in recent_activities:
            raise Exception(recent_activities["error"])

        data = {
            "system_info": system_info,
            "content_stats": content_stats,
            "storage_stats": storage_stats,
            "recent_activities": recent_activities,
        }
        logger.info("系统概览信息获取成功")
        return Response({"code": 0, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取系统概览信息失败", exc_info=True)
        return Response(
            {"code": 1, "message": _("系统处理请求时发生错误")},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def system_info(request):
    """获取系统信息"""
    try:
        logger.debug("获取系统信息...")
        data = SystemService.get_system_info()
        if "error" in data:
            logger.error(f"获取系统信息失败: {data['error']}")
            return Response(
                {"code": 1, "message": _("系统处理请求时发生错误")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"code": 0, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取系统信息失败", exc_info=True)
        return Response(
            {"code": 1, "message": _("系统处理请求时发生错误")},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def content_stats(request):
    """获取内容统计"""
    try:
        logger.debug("获取内容统计...")
        data = SystemService.get_content_stats()
        if "error" in data:
            logger.error(f"获取内容统计失败: {data['error']}")
            return Response(
                {"code": 1, "message": _("系统处理请求时发生错误")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"code": 0, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取内容统计失败", exc_info=True)
        return Response(
            {"code": 1, "message": _("系统处理请求时发生错误")},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def storage_stats(request):
    """获取存储统计"""
    try:
        logger.debug("获取存储统计...")
        data = SystemService.get_storage_stats()
        if "error" in data:
            logger.error(f"获取存储统计失败: {data['error']}")
            return Response(
                {"code": 1, "message": _("系统处理请求时发生错误")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"code": 0, "message": "success", "data": data})
    except Exception as e:
        logger.error("获取存储统计失败", exc_info=True)
        return Response(
            {"code": 1, "message": _("系统处理请求时发生错误")},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
