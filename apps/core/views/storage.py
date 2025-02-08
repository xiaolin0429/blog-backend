import logging

from django.http import HttpResponse

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.storage.factory import StorageFactory

# 获取logger实例
logger = logging.getLogger(__name__)


class FileUploadView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="上传文件",
        operation_description="上传文件到服务器,支持图片、文档和媒体文件",
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="要上传的文件",
            ),
            openapi.Parameter(
                "type",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                description="文件类型(可选):image/document/media,默认自动识别",
            ),
            openapi.Parameter(
                "path",
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                description="保存路径(可选),默认按日期生成",
            ),
        ],
        responses={
            200: openapi.Response("上传成功"),
            400: "请求参数错误",
            401: "未授权",
            403: "无权限上传文件",
            413: "文件大小超出限制",
            415: "不支持的文件类型",
        },
    )
    def post(self, request):
        """上传文件"""
        try:
            # 获取上传的文件
            file = request.FILES.get("file")
            if not file:
                logger.warning("文件上传失败：未提供文件")
                return Response(
                    {"code": 400, "message": "未提供文件"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 验证文件大小
            if not hasattr(file, "size"):
                logger.warning("文件上传失败：无法获取文件大小")
                return Response(
                    {"code": 400, "message": "无效的文件"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 验证文件类型
            if not hasattr(file, "content_type"):
                logger.warning("文件上传失败：无法获取文件类型")
                return Response(
                    {"code": 400, "message": "无效的文件类型"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 获取存储实例
            storage = StorageFactory.get_storage()

            # 上传文件
            result = storage.save_file(
                file=file,
                filename=file.name,
                content_type=file.content_type,
                file_size=file.size,
            )

            logger.info("文件上传成功: %s", file.name)
            return Response({"code": 200, "message": "success", "data": result})

        except ValueError as e:
            logger.warning("文件上传参数错误: %s", str(e))
            return Response(
                {"code": 415, "message": "不支持的文件类型或大小超出限制"},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )
        except PermissionError as e:
            logger.warning("文件上传失败：无权限 - %s", str(e))
            return Response(
                {"code": 403, "message": "无权限上传文件"},
                status=status.HTTP_403_FORBIDDEN,
            )
        except OSError as e:
            logger.error("文件上传失败：系统错误 - %s", str(e))
            return Response(
                {"code": 500, "message": "文件存储失败，请稍后重试"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error("文件上传失败: %s", str(e))
            return Response(
                {"code": 500, "message": "文件上传失败，请稍后重试"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FileDeleteView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="删除文件",
        operation_description="删除指定路径的文件",
        responses={
            200: openapi.Response("删除成功"),
            401: "未授权",
            403: "无权限删除文件",
            404: "文件不存在",
        },
    )
    def delete(self, request, file_id):
        """删除文件"""
        try:
            if not file_id:
                logger.warning("删除文件失败：文件ID为空")
                return Response(
                    {"code": 400, "message": "文件ID不能为空"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            storage = StorageFactory.get_storage()
            if storage.delete_file(file_id):
                logger.info("文件删除成功: %s", file_id)
                return Response({"code": 200, "message": "success"})

            logger.warning("删除文件失败：文件不存在 - %s", file_id)
            return Response(
                {"code": 404, "message": "文件不存在"}, status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            logger.warning("删除文件失败：无权限 - %s", file_id)
            return Response(
                {"code": 403, "message": "无权限删除此文件"},
                status=status.HTTP_403_FORBIDDEN,
            )
        except OSError as e:
            logger.error("删除文件失败：系统错误 - %s", str(e))
            return Response(
                {"code": 500, "message": "文件删除失败，请稍后重试"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error("删除文件失败: %s", str(e))
            return Response(
                {"code": 500, "message": "删除文件失败，请稍后重试"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FileListView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="获取文件列表",
        operation_description="获取已上传的文件列表,支持分页和过滤",
        manual_parameters=[
            openapi.Parameter(
                "path",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="目录路径(可选)",
            ),
            openapi.Parameter(
                "type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="文件类型(可选):all/image/document/media",
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="页码(可选),默认1",
            ),
            openapi.Parameter(
                "size",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="每页数量(可选),默认20,最大100",
            ),
            openapi.Parameter(
                "order_by",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                description="排序字段(可选):name/size/upload_time/type,前缀-表示降序,默认-upload_time",
            ),
        ],
        responses={
            200: openapi.Response("获取成功"),
            400: "请求参数错误",
            401: "未授权",
            403: "无权限查看文件列表",
        },
    )
    def get(self, request):
        """获取文件列表"""
        try:
            # 获取查询参数
            path = request.query_params.get("path")
            file_type = request.query_params.get("type")
            page = int(request.query_params.get("page", 1))
            size = min(int(request.query_params.get("size", 20)), 100)
            order_by = request.query_params.get("order_by", "-upload_time")

            # 获取文件列表
            storage = StorageFactory.get_storage()
            result = storage.get_file_list(
                path=path,
                file_type=file_type,
                page=page,
                page_size=size,
                order_by=order_by,
            )

            return Response({"code": 200, "message": "success", "data": result})

        except ValueError as e:
            logger.warning("获取文件列表参数错误: %s", str(e))
            return Response(
                {"code": 400, "message": "请求参数错误"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error("获取文件列表失败: %s", str(e))
            return Response(
                {"code": 500, "message": "获取文件列表失败，请稍后重试"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FileRenameView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="重命名文件",
        operation_description="重命名已上传的文件",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["new_name"],
            properties={
                "new_name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="新文件名（不包含路径和扩展名）"
                )
            },
        ),
        responses={
            200: openapi.Response("重命名成功"),
            400: "请求参数错误",
            401: "未授权",
            403: "无权限修改文件",
            404: "文件不存在",
            409: "新文件名已存在",
        },
    )
    def put(self, request, file_id):
        """重命名文件"""
        try:
            # 获取并验证新文件名
            new_name = request.data.get("new_name")
            if not new_name:
                logger.warning("重命名文件失败：新文件名为空")
                return Response(
                    {"code": 400, "message": "新文件名不能为空"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 验证新文件名格式
            if "/" in new_name or "\\" in new_name:
                logger.warning("重命名文件失败：文件名包含非法字符 - %s", new_name)
                return Response(
                    {"code": 400, "message": "新文件名不能包含路径分隔符"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 重命名文件
            storage = StorageFactory.get_storage()
            result = storage.rename_file(file_id, new_name)
            return Response({"code": 200, "message": "success", "data": result})

        except ValueError as e:
            logger.warning("重命名文件参数错误: %s", str(e))
            return Response(
                {"code": 400, "message": "文件名格式不正确"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except FileNotFoundError as e:
            logger.warning("重命名文件失败：文件不存在 - %s", file_id)
            return Response(
                {"code": 404, "message": "文件不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except FileExistsError as e:
            logger.warning("重命名文件失败：目标文件名已存在 - %s", new_name)
            return Response(
                {"code": 409, "message": "新文件名已存在"},
                status=status.HTTP_409_CONFLICT,
            )
        except Exception as e:
            logger.error("重命名文件失败: %s", str(e))
            return Response(
                {"code": 500, "message": "重命名文件失败，请稍后重试"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FileContentView(views.APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="获取文件内容",
        operation_description="获取文件的二进制内容",
        responses={
            200: openapi.Response("获取成功"),
            401: "未授权",
            403: "无权限访问文件",
            404: "文件不存在",
        },
    )
    def get(self, request, file_id):
        """获取文件内容"""
        try:
            if not file_id:
                logger.warning("获取文件内容失败：文件ID为空")
                return Response(
                    {"code": 400, "message": "文件ID不能为空"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            storage = StorageFactory.get_storage()
            content, mime_type = storage.get_file_content(file_id)

            if not content:
                logger.warning("获取文件内容失败：文件内容为空 - %s", file_id)
                return Response(
                    {"code": 404, "message": "文件不存在或内容为空"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            response = HttpResponse(content, content_type=mime_type)
            response["Content-Disposition"] = "inline"
            return response

        except ValueError as e:
            logger.warning("获取文件内容参数错误: %s", str(e))
            return Response(
                {"code": 400, "message": "无效的文件ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except FileNotFoundError as e:
            logger.warning("获取文件内容失败：文件不存在 - %s", file_id)
            return Response(
                {"code": 404, "message": "文件不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError as e:
            logger.warning("获取文件内容失败：无权限访问 - %s", file_id)
            return Response(
                {"code": 403, "message": "无权限访问此文件"},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as e:
            logger.error("获取文件内容失败: %s", str(e))
            return Response(
                {"code": 500, "message": "获取文件内容失败，请稍后重试"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
