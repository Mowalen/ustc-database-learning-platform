from __future__ import annotations

from typing import Optional
from datetime import datetime

from pydantic import BaseModel

from app.schemas.users import UserOut


class CourseOut(BaseModel):
    id: int
    title: str
    teacher_id: int
    category_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    teacher: Optional[UserOut] = None
    teacher_name: Optional[str] = None

    class Config:
        from_attributes = True

