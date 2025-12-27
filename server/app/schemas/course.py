from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class CourseCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CourseCategoryCreate(CourseCategoryBase):
    pass

class CourseCategory(CourseCategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

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
    # category: Optional[CourseCategory] = None  # 暂时注释掉，避免异步加载问题

    model_config = ConfigDict(from_attributes=True)

