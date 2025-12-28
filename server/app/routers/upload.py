import os
import uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.routers import get_current_active_user
from app.models.user import User
from app.core.config import BASE_DIR

router = APIRouter()

# 确保上传目录存在
UPLOAD_DIR = os.path.join(str(BASE_DIR), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload_file(upload_file: UploadFile, subfolder: str = "") -> str:
    """
    保存上传的文件到服务器
    
    Args:
        upload_file: 上传的文件对象
        subfolder: 子文件夹名称（如 'images', 'documents' 等）
    
    Returns:
        文件的URL路径
    """
    # 创建子文件夹
    upload_path = os.path.join(UPLOAD_DIR, subfolder)
    os.makedirs(upload_path, exist_ok=True)
    
    # 生成唯一文件名
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_path, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    
    # 返回相对URL路径
    return f"/uploads/{subfolder}/{unique_filename}" if subfolder else f"/uploads/{unique_filename}"


@router.post("/file")
async def upload_file(
    *,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    上传通用文件
    
    - 支持的文件类型：PDF, DOC, DOCX, TXT, ZIP等
    - 最大文件大小：10MB
    """
    # 检查文件大小（10MB限制）
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
    
    # 检查文件类型
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt', '.zip', '.rar', '.xlsx', '.xls', '.ppt', '.pptx'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    file_url = save_upload_file(file, "documents")
    
    return {
        "filename": file.filename,
        "file_url": file_url,
        "file_size": file_size,
        "uploaded_at": datetime.now().isoformat(),
        "uploaded_by": current_user.id
    }


@router.post("/image")
async def upload_image(
    *,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    上传图片文件
    
    - 支持的图片类型：JPG, JPEG, PNG, GIF, WEBP
    - 最大文件大小：5MB
    - 用途：用户头像、课程封面等
    """
    # 检查文件大小（5MB限制）
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    if file_size > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large. Maximum size is 5MB")
    
    # 检查图片类型
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    file_url = save_upload_file(file, "images")
    
    return {
        "filename": file.filename,
        "file_url": file_url,
        "file_size": file_size,
        "uploaded_at": datetime.now().isoformat(),
        "uploaded_by": current_user.id
    }


@router.post("/avatar")
async def upload_avatar(
    *,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    上传用户头像
    
    - 支持的图片类型：JPG, JPEG, PNG
    - 最大文件大小：2MB
    """
    # 检查文件大小（2MB限制）
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB
    if file_size > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="Avatar too large. Maximum size is 2MB")
    
    # 检查图片类型
    allowed_extensions = {'.jpg', '.jpeg', '.png'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    file_url = save_upload_file(file, "avatars")
    
    return {
        "filename": file.filename,
        "file_url": file_url,
        "file_size": file_size,
        "uploaded_at": datetime.now().isoformat(),
        "uploaded_by": current_user.id
    }
