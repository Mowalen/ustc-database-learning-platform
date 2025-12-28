import mimetypes
from pathlib import Path
from typing import Any, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers import get_current_active_user
from app.crud.crud_section import section as crud_section
from app.crud.crud_course import course as crud_course
from app.schemas.section import Section, SectionCreate, SectionUpdate
from app.models.user import User
from app.db.session import get_db

router = APIRouter()

_PDF_DIR = Path("~/tmp/pdf").expanduser()
_VIDEO_DIR = Path("~/tmp/videos").expanduser()

async def _save_upload_file(upload_file: UploadFile, dest_dir: Path) -> str:
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload_file.filename or "").suffix
    filename = f"{uuid4().hex}{suffix}"
    dest_path = dest_dir / filename
    with dest_path.open("wb") as fout:
        while True:
            chunk = await upload_file.read(1024 * 1024)
            if not chunk:
                break
            fout.write(chunk)
    await upload_file.close()
    return str(dest_path)

def _resolve_section_file(path_value: str | None, base_dir: Path) -> Path:
    if not path_value:
        raise HTTPException(status_code=404, detail="File not found")
    path = Path(path_value).expanduser().resolve()
    base = base_dir.resolve()
    if base not in path.parents and path != base:
        raise HTTPException(status_code=404, detail="File not found")
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return path

def _validate_material_file(upload_file: UploadFile) -> None:
    filename = upload_file.filename or ""
    suffix = Path(filename).suffix.lower()
    allowed_exts = {".pdf", ".ppt", ".pptx"}
    allowed_mimes = {
        "application/pdf",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
    if suffix not in allowed_exts and upload_file.content_type not in allowed_mimes:
        raise HTTPException(status_code=400, detail="Material must be a PDF or PPT file")

def _validate_video_file(upload_file: UploadFile) -> None:
    filename = upload_file.filename or ""
    suffix = Path(filename).suffix.lower()
    allowed_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    if suffix not in allowed_exts and not (upload_file.content_type or "").startswith("video/"):
        raise HTTPException(status_code=400, detail="Video must be a valid video file")

@router.get("/courses/{course_id}/sections", response_model=List[Section])
async def read_course_sections(
    *,
    db: AsyncSession = Depends(get_db),
    course_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return await crud_section.get_multi_by_course(db, course_id=course_id, skip=skip, limit=limit)

@router.post("/courses/{course_id}/sections", response_model=Section)
async def create_section(
    *,
    db: AsyncSession = Depends(get_db),
    course_id: int,
    section_in: SectionCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    course = await crud_course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role_id != 3 and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Ensure course_id matches
    if section_in.course_id != course_id:
         raise HTTPException(status_code=400, detail="Course ID mismatch")

    return await crud_section.create(db, obj_in=section_in)

@router.get("/sections/{id}", response_model=Section)
async def read_section(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> Any:
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section

@router.put("/sections/{id}", response_model=Section)
async def update_section(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    section_in: SectionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    course = await crud_course.get(db, id=section.course_id)
    if current_user.role_id != 3 and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    section = await crud_section.update(db, db_obj=section, obj_in=section_in)
    return section

@router.post("/sections/{id}/material", response_model=Section)
async def upload_section_material(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    course = await crud_course.get(db, id=section.course_id)
    if current_user.role_id != 3 and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    _validate_material_file(file)
    saved_path = await _save_upload_file(file, _PDF_DIR)
    section = await crud_section.update(db, db_obj=section, obj_in=SectionUpdate(material_url=saved_path))
    return section

@router.post("/sections/{id}/video", response_model=Section)
async def upload_section_video(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    course = await crud_course.get(db, id=section.course_id)
    if current_user.role_id != 3 and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    _validate_video_file(file)
    saved_path = await _save_upload_file(file, _VIDEO_DIR)
    section = await crud_section.update(db, db_obj=section, obj_in=SectionUpdate(video_url=saved_path))
    return section

@router.get("/sections/{id}/material/download")
async def download_section_material(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> FileResponse:
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    path = _resolve_section_file(section.material_url, _PDF_DIR)
    filename = path.name
    return FileResponse(path, filename=filename, media_type="application/pdf")

@router.get("/sections/{id}/video/stream")
async def stream_section_video(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> FileResponse:
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    path = _resolve_section_file(section.video_url, _VIDEO_DIR)
    media_type, _ = mimetypes.guess_type(str(path))
    return FileResponse(path, media_type=media_type or "application/octet-stream")

@router.delete("/sections/{id}", response_model=Section)
async def delete_section(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    course = await crud_course.get(db, id=section.course_id)
    if current_user.role_id != 3 and course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    section = await crud_section.remove(db, id=id)
    return section
