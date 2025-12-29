from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.routers import require_roles, get_current_active_user
from app.schemas.resources import ResourceOut, ResourceCreate
from app.crud import resources as crud_resources

router = APIRouter()

RESOURCE_DIR = Path(__file__).resolve().parent.parent.parent / "resource"
RESOURCE_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/resources/upload", response_model=ResourceOut)
async def upload_resource(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(2, 3)),  # 仅教师和管理员可上传
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty filename")
    
    # Generate safe filename
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ['.ppt', '.pptx', '.pdf', '.mp4', '.webm', '.ogg']:
        # 您可以根据需要放宽限制，这里仅作基本的PPT和视频检查
        pass 

    safe_name = f"{uuid4().hex}{suffix}"
    file_path = RESOURCE_DIR / safe_name
    
    try:
        content = await file.read()
        file_path.write_bytes(content)
        file_size = len(content)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File save failed") from exc

    # Generate URL
    base_url = str(request.base_url).rstrip("/")
    # 假设我们在 main.py 挂载了 /resources 到 RESOURCE_DIR
    url = f"{base_url}/resources/{safe_name}"

    # Save to DB
    resource_in = ResourceCreate(
        filename=file.filename,
        file_path=str(file_path),
        url=url,
        file_type=suffix, # Or file.content_type
        size_bytes=file_size,
        created_by=current_user.id
    )
    
    resource = await crud_resources.create_resource(db, resource_in)
    return resource

@router.get("/resources/{resource_id}/download")
async def download_resource(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # 登录用户即可下载
):
    resource = await crud_resources.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # 物理路径文件检查
    path = Path(resource.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File on disk not found")
        
    return FileResponse(
        path=path, 
        filename=resource.filename, # 强制下载时使用原始文件名
        media_type='application/octet-stream' # 强制浏览器下载而不是预览（对于PPT）
    )

@router.get("/resources/{resource_id}/play")
async def play_video(
    resource_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    其实前端直接用 url 播放即可，但这个接口可以作为一个带权限检查的代理，
    或者重定向到静态资源URL。这里演示直接返回文件（FileResponse支持Range，适合视频）。
    """
    resource = await crud_resources.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    path = Path(resource.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File on disk not found")
    
    # 对于视频，FileResponse 能够处理 Range header
    return FileResponse(path=path, media_type=resource.file_type or "video/mp4")
