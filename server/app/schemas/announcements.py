from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    created_by: int
    is_active: bool = True


class AnnouncementOut(BaseModel):
    id: int
    title: str
    content: str
    created_by: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

