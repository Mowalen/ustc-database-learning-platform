from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.crud.base import CRUDBase
from app.models.course import Course, CourseCategory
from app.schemas.course import CourseCreate, CourseUpdate, CourseCategoryCreate, CourseCategoryBase

class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    async def get_multi_by_teacher(self, db: AsyncSession, *, teacher_id: int, skip: int = 0, limit: int = 100) -> List[Course]:
        result = await db.execute(select(Course).filter(Course.teacher_id == teacher_id).offset(skip).limit(limit))
        return result.scalars().all()

class CRUDCourseCategory(CRUDBase[CourseCategory, CourseCategoryCreate, CourseCategoryBase]):
    pass

course = CRUDCourse(Course)
category = CRUDCourseCategory(CourseCategory)
