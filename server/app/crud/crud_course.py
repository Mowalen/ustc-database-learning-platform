from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, func, or_
from sqlalchemy.future import select
from app.crud.base import CRUDBase
from app.models.course import Course, CourseCategory
from app.schemas.course import CourseCreate, CourseUpdate, CourseCategoryCreate, CourseCategoryBase

class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    async def get_multi_by_teacher(self, db: AsyncSession, *, teacher_id: int, skip: int = 0, limit: int = 100) -> List[Course]:
        result = await db.execute(select(Course).filter(Course.teacher_id == teacher_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def search_by_title_or_description(
        self,
        db: AsyncSession,
        *,
        query: str,
        limit: int = 10,
    ) -> List[Course]:
        query = query.strip()
        if not query:
            return []

        query_lower = query.lower()
        pattern = f"%{query_lower}%"
        title_lower = func.lower(Course.title)
        desc_lower = func.lower(Course.description)

        match_rank = case(
            (title_lower == query_lower, 0),
            (title_lower.like(f"{query_lower}%"), 1),
            (title_lower.like(pattern), 2),
            (desc_lower.like(pattern), 3),
            else_=4,
        )

        stmt = (
            select(Course)
            .where(
                Course.is_active.is_(True),
                or_(title_lower.like(pattern), desc_lower.like(pattern)),
            )
            .order_by(match_rank, func.length(Course.title), Course.id)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

class CRUDCourseCategory(CRUDBase[CourseCategory, CourseCategoryCreate, CourseCategoryBase]):
    pass

course = CRUDCourse(Course)
category = CRUDCourseCategory(CourseCategory)
