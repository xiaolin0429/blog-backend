from django.utils import timezone

import allure
import pytest
import pytz
from rest_framework import serializers

from apps.core.serializers import TimezoneAwareJSONSerializer, TimezoneSerializerMixin


class TestTimezoneMixinSerializer(TimezoneSerializerMixin, serializers.Serializer):
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    name = serializers.CharField()  # 非日期时间字段


@allure.epic("核心功能")
@allure.feature("时区感知序列化")
@pytest.mark.unit
class TestTimezoneAwareJSONSerializer:
    @allure.story("基础序列化")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试序列化None值的情况")
    @pytest.mark.medium
    def test_none_value(self):
        """测试序列化 None 值"""
        with allure.step("创建序列化器并序列化None值"):
            serializer = TimezoneAwareJSONSerializer()
            assert serializer.to_representation(None) is None

    @allure.story("日期时间序列化")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试序列化无时区信息的日期时间")
    @pytest.mark.high
    def test_naive_datetime(self):
        """测试序列化无时区信息的日期时间"""
        with allure.step("创建无时区日期时间"):
            naive_dt = timezone.datetime(2024, 1, 1, 12, 0)
        
        with allure.step("序列化日期时间"):
            serializer = TimezoneAwareJSONSerializer()
            result = serializer.to_representation(naive_dt)
        
        with allure.step("验证序列化结果"):
            assert result == "2024-01-01T12:00:00"

    @allure.story("日期时间序列化")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试序列化带时区信息的日期时间")
    @pytest.mark.high
    def test_aware_datetime(self):
        """测试序列化带时区信息的日期时间"""
        with allure.step("创建带时区日期时间"):
            tz = pytz.timezone("Asia/Shanghai")
            aware_dt = timezone.datetime(2024, 1, 1, 12, 0, tzinfo=pytz.UTC)
        
        with allure.step("序列化日期时间"):
            serializer = TimezoneAwareJSONSerializer(tz=tz)
            result = serializer.to_representation(aware_dt)
        
        with allure.step("验证序列化结果"):
            assert result == "2024-01-01T20:00:00+08:00"  # UTC+8

    @allure.story("日期时间序列化")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试使用自定义时区进行序列化")
    @pytest.mark.high
    def test_custom_timezone(self):
        """测试使用自定义时区"""
        with allure.step("创建带时区日期时间"):
            tz = pytz.timezone("America/New_York")
            aware_dt = timezone.datetime(2024, 1, 1, 12, 0, tzinfo=pytz.UTC)
        
        with allure.step("序列化日期时间"):
            serializer = TimezoneAwareJSONSerializer(tz=tz)
            result = serializer.to_representation(aware_dt)
        
        with allure.step("验证序列化结果"):
            assert result == "2024-01-01T07:00:00-05:00"  # UTC-5


@allure.epic("核心功能")
@allure.feature("时区感知序列化")
@pytest.mark.unit
class TestTimezoneSerializerMixin:
    @allure.story("默认时区处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试没有请求上下文时的默认时区处理")
    @pytest.mark.high
    def test_no_request_in_context(self):
        """测试没有请求上下文的情况"""
        with allure.step("准备测试数据"):
            data = {
                "created_at": timezone.datetime(2024, 1, 1, 12, 0, tzinfo=pytz.UTC),
                "updated_at": timezone.datetime(2024, 1, 1, 13, 0, tzinfo=pytz.UTC),
                "name": "test",
            }
        
        with allure.step("序列化数据"):
            serializer = TestTimezoneMixinSerializer(data)
            result = serializer.to_representation(data)
        
        with allure.step("验证序列化结果"):
            # 使用默认时区（Asia/Shanghai）
            assert "+08:00" in result["created_at"]
            assert "+08:00" in result["updated_at"]
            assert result["name"] == "test"

    @allure.story("时区请求头处理")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试带有时区请求头的序列化处理")
    @pytest.mark.high
    def test_with_timezone_header(self, rf):
        """测试带有时区请求头的情况"""
        with allure.step("准备请求和测试数据"):
            request = rf.get("/")
            request.headers = {"X-Timezone": "America/New_York"}
            data = {
                "created_at": timezone.datetime(2024, 1, 1, 12, 0, tzinfo=pytz.UTC),
                "updated_at": timezone.datetime(2024, 1, 1, 13, 0, tzinfo=pytz.UTC),
                "name": "test",
            }
        
        with allure.step("序列化数据"):
            serializer = TestTimezoneMixinSerializer(data)
            serializer.context["request"] = request
            result = serializer.to_representation(data)
        
        with allure.step("验证序列化结果"):
            # 验证时区转换（UTC-5）
            assert "-05:00" in result["created_at"]
            assert "-05:00" in result["updated_at"]
            assert result["name"] == "test"

    @allure.story("错误处理")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("测试处理无效时区的情况")
    @pytest.mark.medium
    def test_invalid_timezone(self, rf):
        """测试无效时区的情况"""
        with allure.step("准备带无效时区的请求和测试数据"):
            request = rf.get("/")
            request.headers = {"X-Timezone": "Invalid/Timezone"}
            data = {
                "created_at": timezone.datetime(2024, 1, 1, 12, 0, tzinfo=pytz.UTC),
                "updated_at": timezone.datetime(2024, 1, 1, 13, 0, tzinfo=pytz.UTC),
                "name": "test",
            }
        
        with allure.step("序列化数据"):
            serializer = TestTimezoneMixinSerializer(data)
            serializer.context["request"] = request
            result = serializer.to_representation(data)
        
        with allure.step("验证序列化结果"):
            # 使用默认时区
            assert "+08:00" in result["created_at"]
            assert "+08:00" in result["updated_at"]
            assert result["name"] == "test"

    @allure.story("时区转换")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试无时区日期时间的转换处理")
    @pytest.mark.high
    def test_naive_datetime_conversion(self, rf):
        """测试无时区日期时间的转换"""
        with allure.step("准备请求和无时区测试数据"):
            request = rf.get("/")
            request.headers = {"X-Timezone": "Asia/Shanghai"}
            data = {
                "created_at": timezone.datetime(2024, 1, 1, 12, 0),
                "updated_at": timezone.datetime(2024, 1, 1, 13, 0),
                "name": "test",
            }
        
        with allure.step("序列化数据"):
            serializer = TestTimezoneMixinSerializer(data)
            serializer.context["request"] = request
            result = serializer.to_representation(data)
        
        with allure.step("验证序列化结果"):
            # 验证时区信息被正确添加
            assert "+08:00" in result["created_at"]
            assert "+08:00" in result["updated_at"]
            assert result["name"] == "test"
