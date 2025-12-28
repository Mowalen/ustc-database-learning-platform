from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.session import Base

if TYPE_CHECKING:
    from .course import Course
    from .submission import Submission


class TaskType(str, enum.Enum):
    ASSIGNMENT = "assignment"
    EXAM = "exam"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[TaskType] = mapped_column(
        Enum(TaskType, name="task_type", values_callable=lambda x: [e.value for e in x])
    )
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    course: Mapped["Course"] = relationship(back_populates="tasks")
    submissions: Mapped[list["Submission"]] = relationship(back_populates="task", cascade="all, delete-orphan")
