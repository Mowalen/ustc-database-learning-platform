from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.core.enums import TaskType


class TaskCreate(BaseModel):
    teacher_id: int
    title: str
    description: Optional[str] = None
    type: TaskType
    deadline: Optional[datetime] = None


class TaskOut(BaseModel):
    id: int
    course_id: int
    teacher_id: int
    title: str
    description: Optional[str] = None
    type: TaskType
    deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

