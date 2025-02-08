import os
import uuid
from datetime import datetime
from typing import BinaryIO, List, Optional

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q

from .models.storage import FileStorage


class FileStorageService:
    """文件存储服务"""

    # 支持的文件类型
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        "image/tiff",
        "image/bmp",
        "image/x-icon",
        "image/heic",
        "image/heif",
    }

    ALLOWED_DOCUMENT_TYPES = {
        "application/pdf",
        "application/msword",  # doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
        "application/vnd.ms-excel",  # xls
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
        "application/vnd.ms-powerpoint",  # ppt
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # pptx
        "text/plain",
        "text/markdown",
        "text/csv",
        "application/json",
        "application/xml",
        "text/xml",
        "application/zip",
        "application/x-rar-compressed",
        "application/x-7z-compressed",
    }

    ALLOWED_MEDIA_TYPES = {
        "video/mp4",
        "video/webm",
        "video/x-msvideo",
        "video/quicktime",
        "video/x-matroska",  # 视频
        "audio/mpeg",
        "audio/wav",
        "audio/midi",
        "audio/webm",
        "audio/ogg",
        "audio/aac",  # 音频
        "audio/flac",
        "audio/x-ms-wma",  # 更多音频格式
    }

    # 文件大小限制(字节)
    MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20MB
    MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_MEDIA_SIZE = 200 * 1024 * 1024  # 200MB

    def _get_file_type(self, content_type: str) -> Optional[str]:
        """根据MIME类型判断文件类型"""
        if content_type in self.ALLOWED_IMAGE_TYPES:
            return "image"
        elif content_type in self.ALLOWED_DOCUMENT_TYPES:
            return "document"
        elif content_type in self.ALLOWED_MEDIA_TYPES:
            return "media"
        return None

    def _check_file_size(self, file_size: int, file_type: str) -> bool:
        """检查文件大小是否符合限制"""
        if file_type == "image" and file_size > self.MAX_IMAGE_SIZE:
            return False
        elif file_type == "document" and file_size > self.MAX_DOCUMENT_SIZE:
            return False
        elif file_type == "media" and file_size > self.MAX_MEDIA_SIZE:
            return False
        return True

    def upload_file(
        self, file: BinaryIO, original_filename: str, content_type: str, file_size: int
    ) -> dict:
        """
        上传文件到数据库
        返回: {
            'url': str,      # 文件访问URL
            'path': str,     # 存储ID
            'name': str,     # 文件名
            'original_name': str,  # 原始文件名
            'type': str,     # 文件类型
            'size': int,     # 文件大小
            'mime_type': str,# MIME类型
            'upload_time': str # 上传时间
        }
        """
        try:
            # 检查文件类型
            file_type = self._get_file_type(content_type)
            if not file_type:
                raise ValueError("不支持的文件类型")

            # 检查文件大小
            if not self._check_file_size(file_size, file_type):
                raise ValueError("文件大小超出限制")

            # 生成文件ID
            file_id = uuid.uuid4().hex

            # 读取文件内容
            file_content = file.read()

            # 保存到数据库
            file_obj = FileStorage.objects.create(
                file_id=file_id,
                original_name=original_filename,
                file_type=file_type,
                mime_type=content_type,
                file_size=file_size,
                file_content=file_content,
            )

            return {
                "url": f"/api/v1/storage/files/{file_id}/content",
                "path": file_id,
                "name": original_filename,
                "original_name": original_filename,
                "type": file_type,
                "size": file_size,
                "mime_type": content_type,
                "upload_time": file_obj.created_at.isoformat(),
            }

        except Exception as e:
            raise RuntimeError(f"文件上传失败: {str(e)}")

    def delete_file(self, file_id: str) -> bool:
        """删除文件"""
        try:
            file_obj = FileStorage.objects.filter(file_id=file_id).first()
            if file_obj:
                file_obj.delete()
                return True
            return False
        except Exception:
            return False

    def get_file_list(
        self,
        path: Optional[str] = None,
        file_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "-upload_time",
    ) -> dict:
        """获取文件列表"""
        try:
            # 构建查询条件
            query = Q()
            if file_type and file_type != "all":
                query &= Q(file_type=file_type)

            # 获取文件列表
            queryset = FileStorage.objects.filter(query)

            # 排序
            sort_field = order_by.lstrip("-")
            if sort_field == "upload_time":
                sort_field = "created_at"
            elif sort_field == "name":
                sort_field = "original_name"
            queryset = queryset.order_by(
                f"{'-' if order_by.startswith('-') else ''}{sort_field}"
            )

            # 分页
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)

            # 构建返回数据
            items = []
            for file_obj in page_obj:
                items.append(
                    {
                        "url": f"/api/v1/storage/files/{file_obj.file_id}/content",
                        "path": file_obj.file_id,
                        "name": file_obj.original_name,
                        "original_name": file_obj.original_name,
                        "type": file_obj.file_type,
                        "size": file_obj.file_size,
                        "mime_type": file_obj.mime_type,
                        "upload_time": file_obj.created_at.isoformat(),
                    }
                )

            return {
                "total": paginator.count,
                "page": page,
                "size": page_size,
                "items": items,
            }

        except Exception as e:
            raise RuntimeError(f"获取文件列表失败: {str(e)}")

    def rename_file(self, file_id: str, new_name: str) -> dict:
        """重命名文件"""
        try:
            # 获取文件对象
            file_obj = FileStorage.objects.filter(file_id=file_id).first()
            if not file_obj:
                raise ValueError("原文件不存在")

            # 更新文件名
            file_obj.original_name = new_name
            file_obj.save(update_fields=["original_name", "updated_at"])

            return {
                "url": f"/api/v1/storage/files/{file_obj.file_id}/content",
                "path": file_obj.file_id,
                "name": new_name,
                "original_name": new_name,
                "type": file_obj.file_type,
                "size": file_obj.file_size,
                "mime_type": file_obj.mime_type,
                "upload_time": file_obj.created_at.isoformat(),
            }

        except Exception as e:
            raise RuntimeError(f"重命名文件失败: {str(e)}")

    def get_file_content(self, file_id: str) -> tuple:
        """获取文件内容"""
        try:
            file_obj = FileStorage.objects.filter(file_id=file_id).first()
            if not file_obj:
                raise ValueError("文件不存在")

            return file_obj.file_content, file_obj.mime_type

        except Exception as e:
            raise RuntimeError(f"获取文件内容失败: {str(e)}")
