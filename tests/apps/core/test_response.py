import pytest
from django.utils import timezone
from rest_framework import status
from apps.core.response import (
    APIResponse,
    api_response,
    success_response,
    created_response,
    error_response,
)
from django.test import TestCase

@pytest.mark.unit
class TestAPIResponse(TestCase):
    def test_response_structure(self):
        """测试响应结构"""
        response = success_response(data={"key": "value"})
        self.assertIn('code', response.data)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertIn('timestamp', response.data)
        self.assertIn('requestId', response.data)

    def test_custom_values(self):
        """测试自定义值"""
        response = success_response(
            data={"key": "value"},
            message="custom message"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], "custom message")
        self.assertEqual(response.data['data'], {"key": "value"})

    def test_success_response(self):
        """测试成功响应"""
        response = success_response(data={"key": "value"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], "success")
        self.assertEqual(response.data['data'], {"key": "value"})

    def test_created_response(self):
        """测试创建成功响应"""
        response = created_response(data={'id': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], '创建成功')
        self.assertEqual(response.data['data'], {'id': 1})

    def test_error_response(self):
        """测试错误响应"""
        response = error_response(code=400, message="error message", data={"error": "details"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 400)
        self.assertEqual(response.data['message'], "error message")
        self.assertEqual(response.data['data'], {"error": "details"})

    def test_timestamp_format(self):
        """测试时间戳格式"""
        response = success_response()
        self.assertRegex(response.data['timestamp'], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:\d{2}$')

    def test_request_id_format(self):
        """测试请求ID格式"""
        response = success_response()
        self.assertRegex(response.data['requestId'], r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

    def test_error_response_without_data(self):
        """测试不带数据的错误响应"""
        response = error_response(code=404, message="Not found")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 404)
        self.assertEqual(response.data['message'], "Not found")
        self.assertIsNone(response.data['data'])

    def test_success_response_without_data(self):
        """测试不带数据的成功响应"""
        response = success_response(message="Operation successful")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], "Operation successful")
        self.assertIsNone(response.data['data'])

    def test_error_response_with_validation_errors(self):
        """测试带验证错误的错误响应"""
        validation_errors = {
            "field1": ["This field is required."],
            "field2": ["Invalid value."]
        }
        response = error_response(
            code=400,
            message="Validation failed",
            data={"errors": validation_errors}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 400)
        self.assertEqual(response.data['message'], "Validation failed")
        self.assertEqual(response.data['data']['errors'], validation_errors)

    def test_timestamp_format_old(self):
        """测试时间戳格式"""
        response = APIResponse()
        timestamp = response.data["timestamp"]
        # 验证时间戳是 ISO 格式
        try:
            timezone.datetime.fromisoformat(timestamp)
        except ValueError:
            pytest.fail("Timestamp is not in ISO format")

    def test_request_id_format_old(self):
        """测试请求ID格式"""
        response = APIResponse()
        request_id = response.data["requestId"]
        # 验证请求ID是有效的UUID
        try:
            import uuid
            uuid.UUID(request_id)
        except ValueError:
            pytest.fail("RequestId is not a valid UUID") 