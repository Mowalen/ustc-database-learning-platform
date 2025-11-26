from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import enrollments as crud_enrollments
from app.db.session import get_db
from app.schemas.enrollments import EnrollmentCreate, EnrollmentOut, EnrollmentWithCourse, EnrollmentWithStudent

router = APIRouter(tags=["Enrollments"])


@router.post("/courses/{course_id}/enroll", response_model=EnrollmentOut)
async def enroll(course_id: int, payload: EnrollmentCreate, db: AsyncSession = Depends(get_db)):
    return await crud_enrollments.enroll_student(db, course_id, payload.student_id)


@router.post("/courses/{course_id}/drop", response_model=EnrollmentOut)
async def drop(course_id: int, payload: EnrollmentCreate, db: AsyncSession = Depends(get_db)):
    return await crud_enrollments.drop_course(db, course_id, payload.student_id)


@router.get("/me/enrollments", response_model=list[EnrollmentWithCourse])
async def my_enrollments(student_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_enrollments.list_student_enrollments(db, student_id)


@router.get("/courses/{course_id}/students", response_model=list[EnrollmentWithStudent])
async def course_students(course_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_enrollments.list_course_students(db, course_id)
