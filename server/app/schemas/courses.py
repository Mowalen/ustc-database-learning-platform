from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class CourseOut(BaseModel):
    id: int
    title: str
    teacher_id: int
    category_id: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True

