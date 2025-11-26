from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .enrollment import CourseEnrollment
    from .task import Task


class CourseCategory(Base):
    __tablename__ = "course_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    courses: Mapped[list["Course"]] = relationship(back_populates="category")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    cover_url: Mapped[Optional[str]] = mapped_column(String(255))
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("course_categories.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    teacher: Mapped["User"] = relationship(back_populates="courses_taught", foreign_keys=[teacher_id])
    category: Mapped[Optional["CourseCategory"]] = relationship(back_populates="courses")
    enrollments: Mapped[list["CourseEnrollment"]] = relationship(back_populates="course")
    tasks: Mapped[list["Task"]] = relationship(back_populates="course")
