from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import admin as crud_admin
from app.db.session import get_db
from app.schemas.announcements import AnnouncementCreate, AnnouncementOut
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/users", response_model=UserResponse)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await crud_admin.create_user(db, payload)
    return UserResponse.model_validate(user, from_attributes=True)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db)):
    user = await crud_admin.update_user(db, user_id, payload)
    return UserResponse.model_validate(user, from_attributes=True)


@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud_admin.deactivate_user(db, user_id)
    return UserResponse.model_validate(user, from_attributes=True)


@router.delete("/courses/{course_id}")
async def delete_course(course_id: int, db: AsyncSession = Depends(get_db)):
    course = await crud_admin.deactivate_course(db, course_id)
    return {"course_id": course.id, "is_active": course.is_active}


@router.post("/announcements", response_model=AnnouncementOut)
async def create_announcement(payload: AnnouncementCreate, db: AsyncSession = Depends(get_db)):
    return await crud_admin.create_announcement(db, payload)


@router.get("/announcements", response_model=list[AnnouncementOut])
async def list_announcements(include_inactive: bool = False, db: AsyncSession = Depends(get_db)):
    return await crud_admin.list_announcements(db, include_inactive)


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    role_id: int | None = None,
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户列表（管理员）
    
    - role_id: 按角色筛选（1=student, 2=teacher, 3=admin）
    - include_inactive: 是否包含已停用用户
    - skip: 分页偏移量
    - limit: 分页限制（默认100）
    """
    users = await crud_admin.list_users(db, role_id, include_inactive, skip, limit)
    return [UserResponse.model_validate(user, from_attributes=True) for user in users]


@router.get("/courses")
async def list_all_courses(
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有课程列表（管理员视图）
    
    - include_inactive: 是否包含已下架课程
    - skip: 分页偏移量
    - limit: 分页限制（默认100）
    """
    from app.schemas.course import Course as CourseSchema
    courses = await crud_admin.list_all_courses(db, include_inactive, skip, limit)
    return [CourseSchema.model_validate(course, from_attributes=True) for course in courses]
