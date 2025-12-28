from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.users import UserOut

class CourseCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CourseCategoryCreate(CourseCategoryBase):
    pass

class CourseCategory(CourseCategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    category_id: Optional[int] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    title: Optional[str] = None

class Course(CourseBase):
    id: int
    teacher_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    category: Optional[CourseCategory] = None
    teacher: Optional[UserOut] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True
