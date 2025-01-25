import pytest
import pytz
from django.utils import timezone
from rest_framework import serializers

from apps.core.serializers import TimezoneAwareJSONSerializer, TimezoneSerializerMixin


@pytest.mark.unit
class TestTimezoneAwareJSONSerializer:
    def test_none_value(self):
        """测试序列化 None 值"""
        serializer = TimezoneAwareJSONSerializer()
        assert serializer.to_representation(None) is None

    def test_naive_datetime(self):
        """测试序列化无时区信息的日期时间"""
        naive_dt = timezone.datetime(2024, 1, 1, 12, 0)
        serializer = TimezoneAwareJSONSerializer()
        result = serializer.to_representation(naive_dt)
        assert result == "2024-01-01T12:00:00"

    def test_aware_datetime(self):
        """测试序列化带时区信息的日期时间"""
        tz = pytz.timezone("Asia/Shanghai")
        aware_dt = timezone.datetime(2024, 1, 1, 12, 0, tzinfo=pytz.UTC)
        serializer = TimezoneAwareJSONSerializer(tz=tz)
        result = serializer.to_representation(aware_dt)
        assert result == "2024-01-01T20:00:00+08:00"  # UTC+8

    def test_custom_timezone(self):
        """测试使用自定义时区"""
        tz = pytz.timezone("America/New_York")
        aware_dt = timezone.datetime(2024, 1, 1, 12, 0, tzinfo=pytz.UTC)
        serializer = TimezoneAwareJSONSerializer(tz=tz)
        result = serializer.to_representation(aware_dt)
        assert result == "2024-01-01T07:00:00-05:00"  # UTC-5


@pytest.mark.unit
class TestTimezoneSerializerMixin:
    class TestSerializer(TimezoneSerializerMixin, serializers.Serializer):
        created_at = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()
        name = serializers.CharField()  # 非日期时间字段

    def test_no_request_in_context(self):
        """测试没有请求上下文的情况"""
        data = {
            "created_at": timezone.datetime(2024, 1, 1, 12, 0, tzinfo=pytz.UTC),
            "updated_at": timezone.datetime(2024, 1, 1, 13, 0, tzinfo=pytz.UTC),
            "name": "test",
        }
        serializer = self.TestSerializer(data)
        result = serializer.to_representation(data)
        # 使用默认时区（Asia/Shanghai）
        assert "+08:00" in result["created_at"]
        assert "+08:00" in result["updated_at"]
        assert result["name"] == "test"

    def test_with_timezone_header(self, rf):
        """测试带有时区请求头的情况"""
        request = rf.get("/")
        request.headers = {"X-Timezone": "America/New_York"}
        data = {
            "created_at": timezone.datetime(2024, 1, 1, 12, 0, tzinfo=pytz.UTC),
            "updated_at": timezone.datetime(2024, 1, 1, 13, 0, tzinfo=pytz.UTC),
            "name": "test",
        }
        serializer = self.TestSerializer(data)
        serializer.context["request"] = request
        result = serializer.to_representation(data)
        # 验证时区转换（UTC-5）
        assert "-05:00" in result["created_at"]
        assert "-05:00" in result["updated_at"]
        assert result["name"] == "test"

    def test_invalid_timezone(self, rf):
        """测试无效时区的情况"""
        request = rf.get("/")
        request.headers = {"X-Timezone": "Invalid/Timezone"}
        data = {
            "created_at": timezone.datetime(2024, 1, 1, 12, 0, tzinfo=pytz.UTC),
            "updated_at": timezone.datetime(2024, 1, 1, 13, 0, tzinfo=pytz.UTC),
            "name": "test",
        }
        serializer = self.TestSerializer(data)
        serializer.context["request"] = request
        result = serializer.to_representation(data)
        # 使用默认时区
        assert "+08:00" in result["created_at"]
        assert "+08:00" in result["updated_at"]
        assert result["name"] == "test"

    def test_naive_datetime_conversion(self, rf):
        """测试无时区日期时间的转换"""
        request = rf.get("/")
        request.headers = {"X-Timezone": "Asia/Shanghai"}
        data = {
            "created_at": timezone.datetime(2024, 1, 1, 12, 0),
            "updated_at": timezone.datetime(2024, 1, 1, 13, 0),
            "name": "test",
        }
        serializer = self.TestSerializer(data)
        serializer.context["request"] = request
        result = serializer.to_representation(data)
        # 验证时区信息被正确添加
        assert "+08:00" in result["created_at"]
        assert "+08:00" in result["updated_at"]
        assert result["name"] == "test"
