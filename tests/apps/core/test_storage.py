from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_file_upload(auth_client):
    """测试文件上传"""
    file_content = b"test file content"
    test_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")

    response = auth_client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["code"] == 200
    assert "data" in response.data
    assert "url" in response.data["data"]
    assert response.data["data"]["original_name"] == "test.txt"
    assert response.data["data"]["mime_type"] == "text/plain"
    assert response.data["data"]["size"] == len(file_content)
    assert response.data["data"]["type"] == "document"


def test_file_list(auth_client):
    """测试获取文件列表"""
    # 先上传一个文件
    file_content = b"test file content"
    test_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
    auth_client.post("/api/v1/storage/upload", {"file": test_file}, format="multipart")

    response = auth_client.get("/api/v1/storage/files")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["code"] == 200
    assert "data" in response.data
    assert "items" in response.data["data"]
    assert len(response.data["data"]["items"]) > 0
    assert response.data["data"]["items"][0]["original_name"] == "test.txt"


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


def test_file_rename(auth_client):
    """测试文件重命名"""
    # 先上传一个文件
    file_content = b"test file content"
    test_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
    upload_response = auth_client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )
    file_id = upload_response.data["data"]["path"]

    # 重命名文件
    new_name = "renamed.txt"
    response = auth_client.put(
        f"/api/v1/storage/files/{file_id}/rename", {"new_name": new_name}, format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["code"] == 200
    assert response.data["data"]["original_name"] == new_name


def test_file_rename_nonexistent(auth_client):
    """测试重命名不存在的文件"""
    response = auth_client.put(
        "/api/v1/storage/files/nonexistent/rename",
        {"new_name": "new.txt"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_file_delete(auth_client):
    """测试文件删除"""
    # 先上传一个文件
    file_content = b"test file content"
    test_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
    upload_response = auth_client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )
    file_id = upload_response.data["data"]["path"]

    # 删除文件
    response = auth_client.delete(f"/api/v1/storage/files/{file_id}")
    assert response.status_code == status.HTTP_200_OK

    # 验证文件已被删除
    list_response = auth_client.get("/api/v1/storage/files")
    assert len(list_response.data["data"]["items"]) == 0


def test_file_delete_nonexistent(auth_client):
    """测试删除不存在的文件"""
    response = auth_client.delete("/api/v1/storage/files/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_upload_image(auth_client):
    """测试上传图片文件"""
    image_content = b"fake image content"
    test_file = SimpleUploadedFile("test.jpg", image_content, content_type="image/jpeg")

    response = auth_client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["type"] == "image"
    assert response.data["data"]["mime_type"] == "image/jpeg"


def test_upload_large_file(auth_client):
    """测试上传超大文件"""
    # 创建一个超过图片大小限制的文件（20MB以上）
    large_content = b"x" * (21 * 1024 * 1024)  # 21MB
    test_file = SimpleUploadedFile(
        "large.jpg", large_content, content_type="image/jpeg"
    )

    response = auth_client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )

    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_upload_unsupported_file_type(auth_client):
    """测试上传不支持的文件类型"""
    file_content = b"test content"
    test_file = SimpleUploadedFile(
        "test.xyz", file_content, content_type="application/xyz"
    )

    response = auth_client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )

    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_file_content(auth_client):
    """测试获取文件内容"""
    # 先上传一个文件
    file_content = b"test file content"
    test_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
    upload_response = auth_client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )
    file_id = upload_response.data["data"]["path"]

    # 获取文件内容
    response = auth_client.get(f"/api/v1/storage/files/{file_id}/content")

    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "text/plain"
    assert response.content == file_content


def test_file_content_nonexistent(auth_client):
    """测试获取不存在文件的内容"""
    response = auth_client.get("/api/v1/storage/files/nonexistent/content")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"] == 400
    assert response.data["message"] == "无效的文件ID"


def test_upload_media_files(auth_client):
    """测试上传媒体文件（音频和视频）"""
    # 测试上传MP3
    audio_content = b"fake audio content"
    audio_file = SimpleUploadedFile(
        "test.mp3", audio_content, content_type="audio/mpeg"
    )
    audio_response = auth_client.post(
        "/api/v1/storage/upload", {"file": audio_file}, format="multipart"
    )
    assert audio_response.status_code == status.HTTP_200_OK
    assert audio_response.data["data"]["type"] == "media"
    assert audio_response.data["data"]["mime_type"] == "audio/mpeg"

    # 测试上传MP4
    video_content = b"fake video content"
    video_file = SimpleUploadedFile("test.mp4", video_content, content_type="video/mp4")
    video_response = auth_client.post(
        "/api/v1/storage/upload", {"file": video_file}, format="multipart"
    )
    assert video_response.status_code == status.HTTP_200_OK
    assert video_response.data["data"]["type"] == "media"
    assert video_response.data["data"]["mime_type"] == "video/mp4"


def test_upload_document_files(auth_client):
    """测试上传各种文档类型"""
    # 测试上传PDF
    pdf_content = b"fake pdf content"
    pdf_file = SimpleUploadedFile(
        "test.pdf", pdf_content, content_type="application/pdf"
    )
    pdf_response = auth_client.post(
        "/api/v1/storage/upload", {"file": pdf_file}, format="multipart"
    )
    assert pdf_response.status_code == status.HTTP_200_OK
    assert pdf_response.data["data"]["type"] == "document"

    # 测试上传DOCX
    docx_content = b"fake docx content"
    docx_file = SimpleUploadedFile(
        "test.docx",
        docx_content,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    docx_response = auth_client.post(
        "/api/v1/storage/upload", {"file": docx_file}, format="multipart"
    )
    assert docx_response.status_code == status.HTTP_200_OK
    assert docx_response.data["data"]["type"] == "document"


def test_filename_length_limit(auth_client):
    """测试文件名长度限制"""
    # 测试超长文件名（255字符以上）
    long_filename = "a" * 256 + ".txt"
    file_content = b"test content"
    test_file = SimpleUploadedFile(
        long_filename, file_content, content_type="text/plain"
    )

    response = auth_client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["data"]["original_name"]) <= 255


def test_special_filename(auth_client):
    """测试特殊字符文件名"""
    # 测试包含特殊字符的文件名
    special_filename = "测试文件!@#$%^&*()_+-=[]{}|;'.txt"
    file_content = b"test content"
    test_file = SimpleUploadedFile(
        special_filename, file_content, content_type="text/plain"
    )

    response = auth_client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["original_name"] == special_filename


def test_chinese_filename(auth_client):
    """测试中文文件名"""
    filename = "测试文件.txt"
    file_content = b"test content"
    test_file = SimpleUploadedFile(filename, file_content, content_type="text/plain")

    response = auth_client.post(
        "/api/v1/storage/upload", {"file": test_file}, format="multipart"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["original_name"] == filename


def test_file_list_pagination(auth_client):
    """测试文件列表分页"""
    # 上传多个文件
    for i in range(15):  # 上传15个文件，超过默认的每页10个
        file_content = f"test content {i}".encode()
        test_file = SimpleUploadedFile(
            f"test{i}.txt", file_content, content_type="text/plain"
        )
        auth_client.post(
            "/api/v1/storage/upload", {"file": test_file}, format="multipart"
        )

    # 测试第一页
    response = auth_client.get("/api/v1/storage/files?page=1&size=10")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["data"]["items"]) == 10
    assert response.data["data"]["total"] == 15

    # 测试第二页
    response = auth_client.get("/api/v1/storage/files?page=2&size=10")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["data"]["items"]) == 5


def test_file_list_filter_by_type(auth_client):
    """测试按文件类型筛选文件列表"""
    # 上传不同类型的文件
    text_file = SimpleUploadedFile(
        "test.txt", b"text content", content_type="text/plain"
    )
    image_file = SimpleUploadedFile(
        "test.jpg", b"image content", content_type="image/jpeg"
    )
    pdf_file = SimpleUploadedFile(
        "test.pdf", b"pdf content", content_type="application/pdf"
    )

    auth_client.post("/api/v1/storage/upload", {"file": text_file}, format="multipart")
    auth_client.post("/api/v1/storage/upload", {"file": image_file}, format="multipart")
    auth_client.post("/api/v1/storage/upload", {"file": pdf_file}, format="multipart")

    # 测试筛选文档
    response = auth_client.get("/api/v1/storage/files?type=document")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["data"]["items"]) == 2  # txt和pdf都是文档类型

    # 测试筛选图片
    response = auth_client.get("/api/v1/storage/files?type=image")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["data"]["items"]) == 1


def test_file_list_order_by(auth_client):
    """测试文件列表排序"""
    # 上传两个文件
    file1 = SimpleUploadedFile("aaa.txt", b"content1", content_type="text/plain")
    file2 = SimpleUploadedFile("zzz.txt", b"content2", content_type="text/plain")

    auth_client.post("/api/v1/storage/upload", {"file": file1}, format="multipart")
    auth_client.post("/api/v1/storage/upload", {"file": file2}, format="multipart")

    # 测试按名称升序
    response = auth_client.get("/api/v1/storage/files?order_by=name")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["items"][0]["original_name"] == "aaa.txt"

    # 测试按名称降序
    response = auth_client.get("/api/v1/storage/files?order_by=-name")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["items"][0]["original_name"] == "zzz.txt"
