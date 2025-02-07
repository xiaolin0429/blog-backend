import os
from datetime import datetime
from typing import BinaryIO, List, Optional
from urllib.parse import urljoin

from django.conf import settings

from minio import Minio
from minio.error import S3Error


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

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

        # 确保bucket存在
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

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

    def _generate_file_path(self, original_filename: str, file_type: str) -> str:
        """生成文件存储路径"""
        # 获取文件扩展名
        _, ext = os.path.splitext(original_filename)

        # 生成基于日期的目录结构
        date_path = datetime.now().strftime("%Y/%m/%d")

        # 生成文件名(时间戳+随机字符串)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_str = os.urandom(4).hex()
        filename = f"{timestamp}_{random_str}{ext}"

        return f"{file_type}/{date_path}/{filename}"

    def upload_file(
        self, file: BinaryIO, original_filename: str, content_type: str, file_size: int
    ) -> dict:
        """
        上传文件
        返回: {
            'url': str,      # 文件访问URL
            'path': str,     # 存储路径
            'name': str,     # 文件名
            'original_name': str,  # 原始文件名
            'type': str,     # 文件类型
            'size': int,     # 文件大小
            'mime_type': str,# MIME类型
            'upload_time': str # 上传时间
        }
        """
        # 检查文件类型
        file_type = self._get_file_type(content_type)
        if not file_type:
            raise ValueError("不支持的文件类型")

        # 检查文件大小
        if not self._check_file_size(file_size, file_type):
            raise ValueError("文件大小超出限制")

        # 生成存储路径
        file_path = self._generate_file_path(original_filename, file_type)

        try:
            # 上传文件到MinIO
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_path,
                data=file,
                length=file_size,
                content_type=content_type,
            )

            # 生成访问URL
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name, object_name=file_path
            )

            return {
                "url": url,
                "path": file_path,
                "name": os.path.basename(file_path),
                "original_name": original_filename,
                "type": file_type,
                "size": file_size,
                "mime_type": content_type,
                "upload_time": datetime.now().isoformat(),
            }

        except S3Error as e:
            raise RuntimeError(f"文件上传失败: {str(e)}")

    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            self.client.remove_object(
                bucket_name=self.bucket_name, object_name=file_path
            )
            return True
        except S3Error:
            return False

    def rename_file(self, old_path: str, new_name: str) -> dict:
        """
        重命名文件
        参数:
            old_path: 原文件路径
            new_name: 新文件名（不包含路径和扩展名）
        返回: 更新后的文件信息
        """
        try:
            # 获取原文件信息
            try:
                stat = self.client.stat_object(
                    bucket_name=self.bucket_name, object_name=old_path
                )
            except Exception as e:
                raise ValueError(f"原文件不存在: {str(e)}")

            # 构建新路径（保持原有的目录结构）
            dir_path = os.path.dirname(old_path)
            _, ext = os.path.splitext(old_path)
            new_path = f"{dir_path}/{new_name}{ext}"

            # 检查新文件名是否已存在
            try:
                self.client.stat_object(
                    bucket_name=self.bucket_name, object_name=new_path
                )
                raise RuntimeError("新文件名已存在")
            except Exception as e:
                if not str(e).startswith("新文件名已存在"):
                    pass  # 文件不存在，可以继续重命名

            # 复制文件到新路径
            try:
                source_object = f"{self.bucket_name}/{old_path}"
                self.client.copy_object(
                    bucket_name=self.bucket_name,
                    object_name=new_path,
                    source_bucket_name=self.bucket_name,
                    source_object_name=old_path,
                )
            except Exception as e:
                raise RuntimeError(f"复制文件失败: {str(e)}")

            # 删除原文件
            try:
                self.client.remove_object(
                    bucket_name=self.bucket_name, object_name=old_path
                )
            except Exception as e:
                # 如果删除原文件失败，尝试删除新文件
                try:
                    self.client.remove_object(
                        bucket_name=self.bucket_name, object_name=new_path
                    )
                except:
                    pass
                raise RuntimeError(f"删除原文件失败: {str(e)}")

            # 生成新的访问URL
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name, object_name=new_path
            )

            return {
                "url": url,
                "path": new_path,
                "name": os.path.basename(new_path),
                "original_name": new_name,
                "type": old_path.split("/")[0],
                "size": stat.size,
                "mime_type": stat.content_type,
                "upload_time": stat.last_modified.isoformat(),
            }

        except S3Error as e:
            raise RuntimeError(f"重命名文件失败: {str(e)}")

    def get_file_list(
        self,
        path: Optional[str] = None,
        file_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        order_by: str = "-upload_time",
    ) -> dict:
        """
        获取文件列表
        参数:
            path: 目录路径
            file_type: 文件类型
            page: 页码
            page_size: 每页数量
            order_by: 排序方式
                     支持字段：
                     - name: 按文件名排序
                     - size: 按文件大小排序
                     - upload_time: 按上传时间排序
                     - type: 按文件类型排序
                     前缀-表示降序，如-upload_time
        """
        try:
            # 构建前缀
            prefix = ""
            if file_type and file_type != "all":
                prefix = f"{file_type}/"
            if path:
                prefix = os.path.join(prefix, path)

            # 获取所有对象
            objects = self.client.list_objects(
                bucket_name=self.bucket_name, prefix=prefix, recursive=True
            )

            # 转换为列表并排序
            items = []
            for obj in objects:
                # 获取文件信息
                stat = self.client.stat_object(
                    bucket_name=self.bucket_name, object_name=obj.object_name
                )

                # 生成访问URL
                url = self.client.presigned_get_object(
                    bucket_name=self.bucket_name, object_name=obj.object_name
                )

                items.append(
                    {
                        "url": url,
                        "path": obj.object_name,
                        "name": os.path.basename(obj.object_name),
                        "type": obj.object_name.split("/")[0],
                        "size": stat.size,
                        "mime_type": stat.content_type,
                        "upload_time": stat.last_modified.isoformat(),
                    }
                )

            # 解析排序字段
            sort_field = order_by.lstrip("-")
            reverse = order_by.startswith("-")

            # 根据指定字段排序
            if sort_field == "name":
                items.sort(key=lambda x: x["name"].lower(), reverse=reverse)
            elif sort_field == "size":
                items.sort(key=lambda x: x["size"], reverse=reverse)
            elif sort_field == "type":
                items.sort(key=lambda x: x["type"], reverse=reverse)
            else:  # 默认按上传时间排序
                items.sort(key=lambda x: x["upload_time"], reverse=reverse)

            # 分页
            total = len(items)
            pages = (total + page_size - 1) // page_size
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "total": total,
                "page": page,
                "size": page_size,
                "pages": pages,
                "items": items[start:end],
            }

        except S3Error as e:
            raise RuntimeError(f"获取文件列表失败: {str(e)}")
