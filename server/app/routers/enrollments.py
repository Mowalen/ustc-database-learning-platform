from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import enrollments as crud_enrollments
from app.db.session import get_db
from app.models import Course
from app.models.user import User
from app.routers import get_current_active_user
from app.schemas.enrollments import EnrollmentCreate, EnrollmentOut, EnrollmentWithCourse, EnrollmentWithStudent

router = APIRouter(tags=["Enrollments"])


@router.post("/courses/{course_id}/enroll", response_model=EnrollmentOut)
async def enroll(
    course_id: int,
    payload: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (1, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user.role_id == 1 and payload.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_enrollments.enroll_student(db, course_id, payload.student_id)


@router.post("/courses/{course_id}/drop", response_model=EnrollmentOut)
async def drop(
    course_id: int,
    payload: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (1, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user.role_id == 1 and payload.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_enrollments.drop_course(db, course_id, payload.student_id)


@router.get("/me/enrollments", response_model=list[EnrollmentWithCourse])
async def my_enrollments(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (1, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user.role_id == 1 and student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_enrollments.list_student_enrollments(db, student_id)


@router.get("/courses/{course_id}/students", response_model=list[EnrollmentWithStudent])
async def course_students(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user.role_id == 2:
        course = await db.get(Course, course_id)
        if not course or course.teacher_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_enrollments.list_course_students(db, course_id)
