from rest_framework import serializers
from django.utils import timezone
import pytz

class TimezoneAwareJSONSerializer:
    """
    时区感知的JSON序列化器
    """
    def __init__(self, tz=None):
        self.tz = tz or timezone.get_current_timezone()

    def to_representation(self, value):
        if value is None:
            return None
        if timezone.is_aware(value):
            return value.astimezone(self.tz).isoformat()
        return value.isoformat()

class TimezoneSerializerMixin:
    """
    时区感知的序列化器Mixin
    """
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if request:
            # 从请求头中获取时区信息，如果没有则使用默认时区
            tz_name = request.headers.get('X-Timezone', 'Asia/Shanghai')
            try:
                tz = pytz.timezone(tz_name)
            except pytz.exceptions.UnknownTimeZoneError:
                tz = timezone.get_default_timezone()
            
            # 转换所有日期时间字段
            for field_name, field in self.fields.items():
                if isinstance(field, serializers.DateTimeField):
                    value = ret.get(field_name)
                    if value:
                        dt = timezone.datetime.fromisoformat(value)
                        if timezone.is_naive(dt):
                            dt = timezone.make_aware(dt)
                        ret[field_name] = dt.astimezone(tz).isoformat()
        return ret 