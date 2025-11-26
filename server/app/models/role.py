from __future__ import annotations

import enum
from typing import Optional

from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class RoleName(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[RoleName] = mapped_column(Enum(RoleName, name="role_name"))
    description: Mapped[Optional[str]] = mapped_column(String(100))

    users: Mapped[list["User"]] = relationship(back_populates="role")
