from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.models import RoleName


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role_id: int
    avatar_url: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None
    role_id: Optional[int] = None


class UserOut(UserBase):
    id: int
    role_name: Optional[RoleName] = None

    class Config:
        from_attributes = True

