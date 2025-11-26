from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.crud import enrollments as crud_enrollments
from app.database import get_session

router = APIRouter(tags=["Enrollments"])


@router.post("/courses/{course_id}/enroll", response_model=schemas.EnrollmentOut)
async def enroll(course_id: int, payload: schemas.EnrollmentCreate, session: AsyncSession = Depends(get_session)):
    return await crud_enrollments.enroll_student(session, course_id, payload.student_id)


@router.post("/courses/{course_id}/drop", response_model=schemas.EnrollmentOut)
async def drop(course_id: int, payload: schemas.EnrollmentCreate, session: AsyncSession = Depends(get_session)):
    return await crud_enrollments.drop_course(session, course_id, payload.student_id)


@router.get("/me/enrollments", response_model=list[schemas.EnrollmentWithCourse])
async def my_enrollments(student_id: int, session: AsyncSession = Depends(get_session)):
    return await crud_enrollments.list_student_enrollments(session, student_id)


@router.get("/courses/{course_id}/students", response_model=list[schemas.EnrollmentWithStudent])
async def course_students(course_id: int, session: AsyncSession = Depends(get_session)):
    return await crud_enrollments.list_course_students(session, course_id)
