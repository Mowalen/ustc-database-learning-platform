from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.core.enums import SubmissionStatus


class ScoreOut(BaseModel):
    submission_id: int
    course_id: int
    task_id: int
    task_title: str
    student_id: int
    score: Optional[Decimal]
    feedback: Optional[str] = None
    status: SubmissionStatus
    graded_at: Optional[datetime] = None
