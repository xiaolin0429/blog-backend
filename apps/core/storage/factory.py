from django.conf import settings

from .base import BaseStorage
from .database import DatabaseStorage


class StorageFactory:
    """存储工厂类"""

    @staticmethod
    def get_storage() -> BaseStorage:
        """
        获取存储实例
        根据配置返回对应的存储实现
        """
        storage_backend = getattr(settings, "STORAGE_BACKEND", "database")

        if storage_backend == "database":
            return DatabaseStorage()
        # 后续可以添加其他存储实现
        # elif storage_backend == "minio":
        #     return MinioStorage()
        # elif storage_backend == "oss":
        #     return OssStorage()
        else:
            raise ValueError(f"不支持的存储后端: {storage_backend}")
