from django.test import TestCase
from django.utils import timezone

import allure
import pytest
from rest_framework import status

from apps.core.response import (
    APIResponse,
    api_response,
    created_response,
    error_response,
    success_response,
)


@allure.epic("核心功能")
@allure.feature("API响应")
@pytest.mark.unit
class TestAPIResponse(TestCase):
    @allure.story("响应结构")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("测试API响应的基本结构，包括code、message、data、timestamp和requestId字段")
    @pytest.mark.high
    def test_response_structure(self):
        """测试响应结构"""
        with allure.step("创建成功响应"):
            response = success_response(data={"key": "value"})
        
        with allure.step("验证响应包含所有必需字段"):
            self.assertIn("code", response.data)
            self.assertIn("message", response.data)
            self.assertIn("data", response.data)
            self.assertIn("timestamp", response.data)
            self.assertIn("requestId", response.data)

    @allure.story("响应定制")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试API响应的自定义值，包括自定义消息和数据")
    @pytest.mark.medium
    def test_custom_values(self):
        """测试自定义值"""
        with allure.step("创建带自定义消息的响应"):
            response = success_response(data={"key": "value"}, message="custom message")
        
        with allure.step("验证响应状态码和内容"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["code"], 200)
            self.assertEqual(response.data["message"], "custom message")
            self.assertEqual(response.data["data"], {"key": "value"})

    @allure.story("成功响应")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试标准成功响应的格式和内容")
    @pytest.mark.high
    def test_success_response(self):
        """测试成功响应"""
        with allure.step("创建标准成功响应"):
            response = success_response(data={"key": "value"})
        
        with allure.step("验证响应内容"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["code"], 200)
            self.assertEqual(response.data["message"], "success")
            self.assertEqual(response.data["data"], {"key": "value"})

    @allure.story("创建响应")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试资源创建成功响应的格式和内容")
    @pytest.mark.high
    def test_created_response(self):
        """测试创建成功响应"""
        with allure.step("创建资源成功响应"):
            response = created_response(data={"id": 1})
        
        with allure.step("验证响应内容"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["code"], 200)
            self.assertEqual(response.data["message"], "创建成功")
            self.assertEqual(response.data["data"], {"id": 1})

    @allure.story("错误响应")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试错误响应的格式和内容，包括自定义错误代码和消息")
    @pytest.mark.high
    def test_error_response(self):
        """测试错误响应"""
        with allure.step("创建错误响应"):
            response = error_response(
                code=400, message="error message", data={"error": "details"}
            )
        
        with allure.step("验证响应内容"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["code"], 400)
            self.assertEqual(response.data["message"], "error message")
            self.assertEqual(response.data["data"], {"error": "details"})

    @allure.story("时间戳格式")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试响应中时间戳的格式是否符合ISO标准")
    @pytest.mark.medium
    def test_timestamp_format(self):
        """测试时间戳格式"""
        with allure.step("创建响应并获取时间戳"):
            response = success_response()
        
        with allure.step("验证时间戳格式"):
            self.assertRegex(
                response.data["timestamp"],
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:\d{2}$",
            )

    @allure.story("请求ID格式")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试响应中请求ID的格式是否符合UUID标准")
    @pytest.mark.medium
    def test_request_id_format(self):
        """测试请求ID格式"""
        with allure.step("创建响应并获取请求ID"):
            response = success_response()
        
        with allure.step("验证请求ID格式"):
            self.assertRegex(
                response.data["requestId"],
                r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            )

    @allure.story("错误响应")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试不带数据的错误响应格式")
    @pytest.mark.medium
    def test_error_response_without_data(self):
        """测试不带数据的错误响应"""
        with allure.step("创建不带数据的错误响应"):
            response = error_response(code=404, message="Not found")
        
        with allure.step("验证响应内容"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["code"], 404)
            self.assertEqual(response.data["message"], "Not found")
            self.assertIsNone(response.data["data"])

    @allure.story("成功响应")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试不带数据的成功响应格式")
    @pytest.mark.medium
    def test_success_response_without_data(self):
        """测试不带数据的成功响应"""
        with allure.step("创建不带数据的成功响应"):
            response = success_response(message="Operation successful")
        
        with allure.step("验证响应内容"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["code"], 200)
            self.assertEqual(response.data["message"], "Operation successful")
            self.assertIsNone(response.data["data"])

    @allure.story("错误响应")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试带验证错误的错误响应格式和内容")
    @pytest.mark.high
    def test_error_response_with_validation_errors(self):
        """测试带验证错误的错误响应"""
        with allure.step("准备验证错误数据"):
            validation_errors = {
                "field1": ["This field is required."],
                "field2": ["Invalid value."],
            }
        
        with allure.step("创建带验证错误的错误响应"):
            response = error_response(
                code=400, message="Validation failed", data={"errors": validation_errors}
            )
        
        with allure.step("验证响应内容"):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["code"], 400)
            self.assertEqual(response.data["message"], "Validation failed")
            self.assertEqual(response.data["data"]["errors"], validation_errors)

    @allure.story("时间戳格式")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试时间戳格式是否可以被解析为有效的ISO格式")
    @pytest.mark.medium
    def test_timestamp_format_old(self):
        """测试时间戳格式"""
        with allure.step("创建响应并获取时间戳"):
            response = APIResponse()
            timestamp = response.data["timestamp"]
        
        with allure.step("验证时间戳是否为ISO格式"):
            try:
                timezone.datetime.fromisoformat(timestamp)
            except ValueError:
                pytest.fail("Timestamp is not in ISO format")

    @allure.story("请求ID格式")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试请求ID是否为有效的UUID格式")
    @pytest.mark.medium
    def test_request_id_format_old(self):
        """测试请求ID格式"""
        with allure.step("创建响应并获取请求ID"):
            response = APIResponse()
            request_id = response.data["requestId"]
        
        with allure.step("验证请求ID是否为有效的UUID"):
            try:
                import uuid
                uuid.UUID(request_id)
            except ValueError:
                pytest.fail("RequestId is not a valid UUID")
