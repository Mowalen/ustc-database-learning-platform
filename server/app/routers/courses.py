from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers import get_current_active_user
from app.crud.crud_course import course as crud_course, category as crud_category
from app.schemas.course import Course, CourseCreate, CourseUpdate, CourseCategory, CourseCategoryCreate
from app.models.user import User
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[Course])
async def read_courses(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return await crud_course.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=Course)
async def create_course(
    *,
    db: AsyncSession = Depends(get_db),
    course_in: CourseCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    # TODO: Check if user is teacher
    # if current_user.role_id != TEACHER_ROLE_ID:
    #     raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Manually set teacher_id since it's not in CourseCreate
    # We need to override the create method or handle it here
    # Since CRUDBase.create takes obj_in, we need to add teacher_id to it or the model
    # But obj_in is Pydantic.
    
    # Let's do it manually here for now or update CRUD
    obj_in_data = course_in.dict()
    obj_in_data["teacher_id"] = current_user.id
    db_obj = crud_course.model(**obj_in_data)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.get("/{id}", response_model=Course)
async def read_course(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> Any:
    course = await crud_course.get(db, id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{id}", response_model=Course)
async def update_course(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    course_in: CourseUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    course = await crud_course.get(db, id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != current_user.id: # and not superuser
         raise HTTPException(status_code=400, detail="Not enough permissions")
    course = await crud_course.update(db, db_obj=course, obj_in=course_in)
    return course

@router.delete("/{id}", response_model=Course)
async def delete_course(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    course = await crud_course.get(db, id=id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != current_user.id:
         raise HTTPException(status_code=400, detail="Not enough permissions")
    course = await crud_course.remove(db, id=id)
    return course

# Categories
@router.get("/categories/", response_model=List[CourseCategory])
async def read_categories(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return await crud_category.get_multi(db, skip=skip, limit=limit)

@router.post("/categories/", response_model=CourseCategory)
async def create_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_in: CourseCategoryCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    # Check admin permission
    return await crud_category.create(db, obj_in=category_in)
