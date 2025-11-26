from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SectionBase(BaseModel):
    title: str
    content: Optional[str] = None
    material_url: Optional[str] = None
    video_url: Optional[str] = None
    order_index: Optional[int] = 0

class SectionCreate(SectionBase):
    course_id: int

class SectionUpdate(SectionBase):
    title: Optional[str] = None

class Section(SectionBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
