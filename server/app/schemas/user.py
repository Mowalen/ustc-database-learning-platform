from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.role import Role

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str
    role_id: int

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    role: Optional[Role] = None

    class Config:
        from_attributes = True
