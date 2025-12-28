from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models import EnrollmentStatus
from .courses import CourseOut
from .users import UserOut


class EnrollmentCreate(BaseModel):
    student_id: int


class EnrollmentOut(BaseModel):
    id: int
    course_id: int
    student_id: int
    status: EnrollmentStatus
    enrolled_at: datetime

    class Config:
        from_attributes = True


class EnrollmentWithCourse(EnrollmentOut):
    course: CourseOut


class EnrollmentWithStudent(EnrollmentOut):
    student: UserOut

