from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from app.crud import admin as crud_admin
from app.db.mysql_pool import get_db_cursor
from app.routers import get_current_active_user, require_roles
from app.schemas.announcements import AnnouncementCreate, AnnouncementOut
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/users", response_model=UserResponse)
async def create_user(
    payload: UserCreate,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(require_roles(3)),
):
    cursor, conn = cursor_conn
    user_data = jsonable_encoder(payload)
    return await crud_admin.create_user(cursor, conn, user_data)


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(require_roles(3)),
):
    cursor, conn = cursor_conn
    return await crud_admin.list_users(cursor, skip=skip, limit=limit, role_id=role_id, is_active=is_active)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(require_roles(3)),
):
    cursor, conn = cursor_conn
    user_data = jsonable_encoder(payload)
    return await crud_admin.update_user(cursor, conn, user_id, user_data)


@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(require_roles(3)),
):
    cursor, conn = cursor_conn
    return await crud_admin.deactivate_user(cursor, conn, user_id)


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(require_roles(3)),
):
    cursor, conn = cursor_conn
    course = await crud_admin.deactivate_course(cursor, conn, course_id)
    return {"course_id": course['id'], "is_active": course['is_active']}


@router.post("/announcements", response_model=AnnouncementOut)
async def create_announcement(
    payload: AnnouncementCreate,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(require_roles(3)),
):
    cursor, conn = cursor_conn
    announcement_data = jsonable_encoder(payload)
    return await crud_admin.create_announcement(cursor, conn, announcement_data)


@router.get("/announcements", response_model=List[AnnouncementOut])
async def list_announcements(
    include_inactive: bool = False,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if include_inactive and current_user['role_id'] != 3:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud_admin.list_announcements(cursor, include_inactive)
