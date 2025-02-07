from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..storage import FileStorageService


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
                return Response(
                    {"code": 400, "message": "未提供文件"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 创建存储服务
            storage = FileStorageService()

            # 上传文件
            result = storage.upload_file(
                file=file,
                original_filename=file.name,
                content_type=file.content_type,
                file_size=file.size,
            )

            return Response({"code": 200, "message": "success", "data": result})

        except ValueError as e:
            return Response(
                {"code": 415, "message": str(e)},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )
        except RuntimeError as e:
            return Response(
                {"code": 500, "message": str(e)},
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
    def delete(self, request, path):
        """删除文件"""
        try:
            storage = FileStorageService()
            if storage.delete_file(path):
                return Response({"code": 200, "message": "success"})
            return Response(
                {"code": 404, "message": "文件不存在"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": str(e)},
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
            storage = FileStorageService()
            result = storage.get_file_list(
                path=path,
                file_type=file_type,
                page=page,
                page_size=size,
                order_by=order_by,
            )

            return Response({"code": 200, "message": "success", "data": result})

        except ValueError:
            return Response(
                {"code": 400, "message": "参数错误"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": str(e)},
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
    def put(self, request, path):
        """重命名文件"""
        try:
            # 获取并验证新文件名
            new_name = request.data.get("new_name")
            if not new_name:
                return Response(
                    {"code": 400, "message": "新文件名不能为空"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 验证新文件名格式
            if "/" in new_name or "\\" in new_name:
                return Response(
                    {"code": 400, "message": "新文件名不能包含路径分隔符"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 创建存储服务
            storage = FileStorageService()

            try:
                # 检查文件是否存在
                storage.client.stat_object(
                    bucket_name=storage.bucket_name, object_name=path
                )
            except Exception:
                return Response(
                    {"code": 404, "message": "文件不存在"}, status=status.HTTP_404_NOT_FOUND
                )

            try:
                # 重命名文件
                result = storage.rename_file(path, new_name)
                return Response({"code": 200, "message": "success", "data": result})
            except RuntimeError as e:
                if "已存在" in str(e):
                    return Response(
                        {"code": 409, "message": "新文件名已存在"},
                        status=status.HTTP_409_CONFLICT,
                    )
                raise

        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"code": 500, "message": f"重命名文件失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
