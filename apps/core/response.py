from rest_framework.response import Response
from rest_framework import status
import uuid
from django.utils import timezone

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
            "requestId": str(uuid.uuid4())
        }
        super().__init__(data=response_data, **kwargs)

def api_response(code=200, message="success", data=None, status_code=None):
    """
    创建标准API响应的快捷方法
    """
    return APIResponse(code=code, message=message, data=data, status=status_code or status.HTTP_200_OK)

def success_response(data=None, message="success"):
    """
    成功响应
    """
    return api_response(code=200, message=message, data=data)

def created_response(data=None, message="created"):
    """
    创建成功响应
    """
    return api_response(code=201, message=message, data=data, status_code=status.HTTP_201_CREATED)

def error_response(code, message, data=None, status_code=None):
    """
    错误响应
    """
    return api_response(code=code, message=message, data=data, status_code=status_code) 