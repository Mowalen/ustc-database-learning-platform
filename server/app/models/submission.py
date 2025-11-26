from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

if TYPE_CHECKING:
    from .task import Task
    from .user import User


class SubmissionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    GRADED = "graded"
    LATE = "late"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    answer_text: Mapped[Optional[str]] = mapped_column(Text)
    file_url: Mapped[Optional[str]] = mapped_column(String(255))
    score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    graded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status"), default=SubmissionStatus.SUBMITTED
    )

    task: Mapped["Task"] = relationship(back_populates="submissions")
    student: Mapped["User"] = relationship(back_populates="submissions")

