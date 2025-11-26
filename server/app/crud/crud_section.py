from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.crud.base import CRUDBase
from app.models.section import CourseSection
from app.schemas.section import SectionCreate, SectionUpdate

class CRUDSection(CRUDBase[CourseSection, SectionCreate, SectionUpdate]):
    async def get_multi_by_course(self, db: AsyncSession, *, course_id: int, skip: int = 0, limit: int = 100) -> List[CourseSection]:
        result = await db.execute(select(CourseSection).filter(CourseSection.course_id == course_id).order_by(CourseSection.order_index).offset(skip).limit(limit))
        return result.scalars().all()

section = CRUDSection(CourseSection)
