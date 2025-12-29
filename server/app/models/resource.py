from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.session import Base

class Resource(Base):
    __tablename__ = "server_resources"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)  # 物理路径
    url = Column(String(512), nullable=False)       # 访问 URL
    file_type = Column(String(50))                  # mime type 或 simple type (ppt/video)
    size_bytes = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")
