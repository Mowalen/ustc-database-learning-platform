"""
Tests for file upload endpoints
"""
import pytest
import io
from httpx import AsyncClient
from typing import Dict


@pytest.mark.asyncio
async def test_upload_file_without_auth(client: AsyncClient):
    """测试未认证时上传文件应失败"""
    # Create a fake file
    files = {"file": ("test.pdf", io.BytesIO(b"fake pdf content"), "application/pdf")}
    
    response = await client.post("/upload/file", files=files)
    
    # Should require authentication
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_file_success(client: AsyncClient, teacher_headers: Dict[str, str]):
    """测试成功上传通用文件"""
    # Create a fake PDF file
    file_content = b"This is a test PDF file content"
    files = {"file": ("test_document.pdf", io.BytesIO(file_content), "application/pdf")}
    
    response = await client.post(
        "/upload/file",
        files=files,
        headers=teacher_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "file_url" in data
    assert "file_size" in data
    assert "uploaded_at" in data
    assert "uploaded_by" in data
    assert data["filename"] == "test_document.pdf"
    assert "/uploads/documents/" in data["file_url"]


@pytest.mark.asyncio
async def test_upload_file_invalid_type(client: AsyncClient, teacher_headers: Dict[str, str]):
    """测试上传不支持的文件类型"""
    # Create a fake file with unsupported extension
    file_content = b"This is a test file"
    files = {"file": ("test.exe", io.BytesIO(file_content), "application/octet-stream")}
    
    response = await client.post(
        "/upload/file",
        files=files,
        headers=teacher_headers
    )
    
    assert response.status_code == 400
    assert "Invalid file type" in response.text


@pytest.mark.asyncio
async def test_upload_image_success(client: AsyncClient, teacher_headers: Dict[str, str]):
    """测试成功上传图片"""
    # Create a fake image file (minimal valid PNG header)
    png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
    files = {"file": ("test_image.png", io.BytesIO(png_header), "image/png")}
    
    response = await client.post(
        "/upload/image",
        files=files,
        headers=teacher_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "file_url" in data
    assert data["filename"] == "test_image.png"
    assert "/uploads/images/" in data["file_url"]


@pytest.mark.asyncio
async def test_upload_image_invalid_type(client: AsyncClient, teacher_headers: Dict[str, str]):
    """测试上传非图片文件到图片接口"""
    file_content = b"This is not an image"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    
    response = await client.post(
        "/upload/image",
        files=files,
        headers=teacher_headers
    )
    
    assert response.status_code == 400
    assert "Invalid image type" in response.text


@pytest.mark.asyncio
async def test_upload_avatar_success(client: AsyncClient, student_headers: Dict[str, str]):
    """测试成功上传头像"""
    # Create a fake JPEG file
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF'
    files = {"file": ("avatar.jpg", io.BytesIO(jpeg_header), "image/jpeg")}
    
    response = await client.post(
        "/upload/avatar",
        files=files,
        headers=student_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "file_url" in data
    assert data["filename"] == "avatar.jpg"
    assert "/uploads/avatars/" in data["file_url"]


@pytest.mark.asyncio
async def test_upload_avatar_invalid_type(client: AsyncClient, student_headers: Dict[str, str]):
    """测试上传不支持的头像格式"""
    file_content = b"GIF89a"  # GIF format not allowed for avatars
    files = {"file": ("avatar.gif", io.BytesIO(file_content), "image/gif")}
    
    response = await client.post(
        "/upload/avatar",
        files=files,
        headers=student_headers
    )
    
    assert response.status_code == 400
    assert "Invalid image type" in response.text


@pytest.mark.asyncio
async def test_upload_multiple_file_types(client: AsyncClient, teacher_headers: Dict[str, str]):
    """测试上传多种支持的文件类型"""
    supported_files = [
        ("document.pdf", "application/pdf"),
        ("document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ("spreadsheet.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        ("archive.zip", "application/zip"),
        ("text.txt", "text/plain"),
    ]
    
    for filename, mime_type in supported_files:
        file_content = b"Test content for " + filename.encode()
        files = {"file": (filename, io.BytesIO(file_content), mime_type)}
        
        response = await client.post(
            "/upload/file",
            files=files,
            headers=teacher_headers
        )
        
        assert response.status_code == 200, f"Failed to upload {filename}"
        data = response.json()
        assert data["filename"] == filename
