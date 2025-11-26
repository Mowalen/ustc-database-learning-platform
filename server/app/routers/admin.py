from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.crud import admin as crud_admin
from app.database import get_session

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/users", response_model=schemas.UserOut)
async def create_user(payload: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    user = await crud_admin.create_user(session, payload)
    return schemas.UserOut.model_validate(user, from_attributes=True)


@router.put("/users/{user_id}", response_model=schemas.UserOut)
async def update_user(user_id: int, payload: schemas.UserUpdate, session: AsyncSession = Depends(get_session)):
    user = await crud_admin.update_user(session, user_id, payload)
    return schemas.UserOut.model_validate(user, from_attributes=True)


@router.delete("/users/{user_id}", response_model=schemas.UserOut)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await crud_admin.deactivate_user(session, user_id)
    return schemas.UserOut.model_validate(user, from_attributes=True)


@router.delete("/courses/{course_id}")
async def delete_course(course_id: int, session: AsyncSession = Depends(get_session)):
    course = await crud_admin.deactivate_course(session, course_id)
    return {"course_id": course.id, "is_active": course.is_active}


@router.post("/announcements", response_model=schemas.AnnouncementOut)
async def create_announcement(payload: schemas.AnnouncementCreate, session: AsyncSession = Depends(get_session)):
    return await crud_admin.create_announcement(session, payload)


@router.get("/announcements", response_model=list[schemas.AnnouncementOut])
async def list_announcements(include_inactive: bool = False, session: AsyncSession = Depends(get_session)):
    return await crud_admin.list_announcements(session, include_inactive)
