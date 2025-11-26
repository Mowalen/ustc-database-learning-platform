from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .role import Role, RoleName

if TYPE_CHECKING:
    from .course import Course
    from .enrollment import CourseEnrollment
    from .submission import Submission
    from .announcement import Announcement


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role: Mapped["Role"] = relationship(back_populates="users")
    courses_taught: Mapped[list["Course"]] = relationship(
        back_populates="teacher", foreign_keys="Course.teacher_id"
    )
    enrollments: Mapped[list["CourseEnrollment"]] = relationship(back_populates="student")
    submissions: Mapped[list["Submission"]] = relationship(back_populates="student")
    announcements: Mapped[list["Announcement"]] = relationship(back_populates="creator")

    @property
    def role_name(self) -> Optional[RoleName]:
        return self.role.name if self.role else None

