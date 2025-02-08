from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, List, Optional, Tuple


class BaseStorage(ABC):
    """存储接口抽象类"""

    @abstractmethod
    def save_file(
        self, file: BinaryIO, filename: str, content_type: str, file_size: int
    ) -> Dict:
        """
        保存文件
        Args:
            file: 文件对象
            filename: 文件名
            content_type: 文件类型
            file_size: 文件大小
        Returns:
            Dict: {
                'url': str,           # 文件访问URL
                'path': str,          # 存储路径/ID
                'name': str,          # 文件名
                'original_name': str,  # 原始文件名
                'type': str,          # 文件类型
                'size': int,          # 文件大小
                'mime_type': str,     # MIME类型
                'upload_time': str    # 上传时间
            }
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        Args:
            file_path: 文件路径/ID
        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    def get_file_list(
        self,
        path: Optional[str] = None,
        file_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "-upload_time",
    ) -> Dict:
        """
        获取文件列表
        Args:
            path: 目录路径
            file_type: 文件类型
            page: 页码
            page_size: 每页数量
            order_by: 排序字段
        Returns:
            Dict: {
                'total': int,    # 总数
                'page': int,     # 当前页
                'size': int,     # 每页数量
                'items': List    # 文件列表
            }
        """
        pass

    @abstractmethod
    def rename_file(self, file_path: str, new_name: str) -> Dict:
        """
        重命名文件
        Args:
            file_path: 文件路径/ID
            new_name: 新文件名
        Returns:
            Dict: 文件信息
        """
        pass

    @abstractmethod
    def get_file_content(self, file_path: str) -> Tuple[bytes, str]:
        """
        获取文件内容
        Args:
            file_path: 文件路径/ID
        Returns:
            Tuple[bytes, str]: (文件内容, MIME类型)
        """
        pass
