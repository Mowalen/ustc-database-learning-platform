from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Request
from starlette import status

from app.models.user import User
from app.routers import require_roles
from app.schemas.uploads import UploadResponse

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/uploads", response_model=UploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(2, 3)),
) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty filename")
    suffix = Path(file.filename).suffix.lower()
    safe_name = f"{uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / safe_name
    try:
        contents = await file.read()
        destination.write_bytes(contents)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Upload failed") from exc
    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}/uploads/{safe_name}"
    return UploadResponse(url=url, filename=file.filename)
