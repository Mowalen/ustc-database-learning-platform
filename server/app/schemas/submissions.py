from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.core.enums import SubmissionStatus
from app.schemas.users import UserOut


class SubmissionCreate(BaseModel):
    student_id: int
    answer_text: Optional[str] = None
    file_url: Optional[str] = None


class SubmissionOut(BaseModel):
    id: int
    task_id: int
    student_id: int
    answer_text: Optional[str] = None
    file_url: Optional[str] = None
    score: Optional[Decimal] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None
    status: SubmissionStatus

    class Config:
        from_attributes = True


class GradeUpdate(BaseModel):
    score: Decimal
    feedback: Optional[str] = None
    status: Optional[SubmissionStatus] = SubmissionStatus.GRADED


class SubmissionWithStudent(SubmissionOut):
    student: UserOut

    class Config:
        from_attributes = True
