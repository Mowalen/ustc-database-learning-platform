from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.course import Course, CourseCategory
from app.schemas.course import CourseCreate, CourseUpdate, CourseCategoryCreate, CourseCategoryBase

class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    async def get(self, db: AsyncSession, id: int) -> Optional[Course]:
        result = await db.execute(
            select(Course)
            .options(selectinload(Course.teacher), selectinload(Course.category))
            .filter(Course.id == id)
        )
        return result.scalars().first()

    async def get_multi_by_teacher(self, db: AsyncSession, *, teacher_id: int, skip: int = 0, limit: int = 100) -> List[Course]:
        result = await db.execute(
            select(Course)
            .options(selectinload(Course.teacher), selectinload(Course.category))
            .filter(Course.teacher_id == teacher_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Course]:
        result = await db.execute(
            select(Course)
            .options(selectinload(Course.teacher), selectinload(Course.category))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

class CRUDCourseCategory(CRUDBase[CourseCategory, CourseCategoryCreate, CourseCategoryBase]):
    pass

course = CRUDCourse(Course)
category = CRUDCourseCategory(CourseCategory)
