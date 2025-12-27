from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import admin as crud_admin
from app.db.session import get_db
from app.models.user import User
from app.routers import get_current_active_user, require_roles
from app.schemas.announcements import AnnouncementCreate, AnnouncementOut
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/users", response_model=UserResponse)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(3)),
):
    user = await crud_admin.create_user(db, payload)
    return UserResponse.model_validate(user, from_attributes=True)

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role_id: int | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(3)),
):
    users = await crud_admin.list_users(db, skip=skip, limit=limit, role_id=role_id, is_active=is_active)
    return [UserResponse.model_validate(user, from_attributes=True) for user in users]


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(3)),
):
    user = await crud_admin.update_user(db, user_id, payload)
    return UserResponse.model_validate(user, from_attributes=True)


@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(3)),
):
    user = await crud_admin.deactivate_user(db, user_id)
    return UserResponse.model_validate(user, from_attributes=True)


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(3)),
):
    course = await crud_admin.deactivate_course(db, course_id)
    return {"course_id": course.id, "is_active": course.is_active}


@router.post("/announcements", response_model=AnnouncementOut)
async def create_announcement(
    payload: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(3)),
):
    return await crud_admin.create_announcement(db, payload)


@router.get("/announcements", response_model=list[AnnouncementOut])
async def list_announcements(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if include_inactive and current_user.role_id != 3:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud_admin.list_announcements(db, include_inactive)
