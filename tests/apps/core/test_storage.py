from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_file_upload(auth_client):
    """测试文件上传"""
    file_content = b"test file content"
    test_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")

    with patch("apps.core.storage.Minio") as mock_minio:
        # 配置mock的行为
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_client.put_object.return_value = None
        mock_client.presigned_get_object.return_value = "http://test-url/test.txt"
        mock_minio.return_value = mock_client

        response = auth_client.post(
            "/api/v1/storage/upload", {"file": test_file}, format="multipart"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert "data" in response.data
        assert "url" in response.data["data"]


def test_file_list(auth_client):
    """测试获取文件列表"""
    with patch("apps.core.storage.Minio") as mock_minio:
        # 配置mock的行为
        mock_client = MagicMock()
        mock_client.bucket_exists.return_value = True
        mock_client.list_objects.return_value = []
        mock_minio.return_value = mock_client

        response = auth_client.get("/api/v1/storage/files")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == 200
        assert "data" in response.data
        assert "items" in response.data["data"]


def test_file_upload_no_file(auth_client):
    """测试上传时未提供文件"""
    response = auth_client.post("/api/v1/storage/upload", {}, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"] == 400


def test_file_upload_unauthorized(client):
    """测试未授权用户上传文件"""
    file_content = b"test file content"
    test_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")

    response = client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
