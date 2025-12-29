from datetime import datetime
from pydantic import BaseModel

class ResourceBase(BaseModel):
    filename: str
    file_type: str

class ResourceCreate(ResourceBase):
    file_path: str
    url: str
    size_bytes: int
    created_by: int

class ResourceOut(ResourceBase):
    id: int
    url: str
    created_at: datetime
    size_bytes: int

    class Config:
        from_attributes = True
