import uuid

from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response


class APIResponse(Response):
    """
    标准API响应类
    """

    def __init__(self, code=200, message="success", data=None, **kwargs):
        response_data = {
            "code": code,
            "message": message,
            "data": data,
            "timestamp": timezone.now().isoformat(),
            "requestId": str(uuid.uuid4()),
        }
        # 所有业务响应都返回200状态码
        if "status" not in kwargs:
            kwargs["status"] = status.HTTP_200_OK

        super().__init__(data=response_data, **kwargs)


def api_response(code=200, message="success", data=None, status_code=None):
    """
    创建标准API响应的快捷方法
    """
    # 所有业务响应都返回200状态码
    if status_code is None:
        status_code = status.HTTP_200_OK
    return APIResponse(code=code, message=message, data=data, status=status_code)


def success_response(data=None, message="success", code=200, status_code=None):
    """
    成功响应
    """
    return api_response(code=code, message=message, data=data, status_code=status_code)


def created_response(data=None, message="创建成功"):
    """
    创建成功响应
    """
    return api_response(code=200, message=message, data=data)


def error_response(code, message, data=None, status_code=None):
    """
    错误响应
    """
    return api_response(code=code, message=message, data=data, status_code=status_code)
