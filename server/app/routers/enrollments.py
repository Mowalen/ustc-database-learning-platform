from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.crud import enrollments as crud_enrollments
from app.crud import crud_course
from app.db.mysql_pool import get_db_cursor
from app.routers import get_current_active_user
from app.schemas.enrollments import EnrollmentCreate, EnrollmentOut, EnrollmentWithCourse, EnrollmentWithStudent

router = APIRouter(tags=["Enrollments"])


@router.post("/courses/{course_id}/enroll", response_model=EnrollmentOut)
async def enroll(
    course_id: int,
    payload: EnrollmentCreate,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (1, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user['role_id'] == 1 and payload.student_id != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_enrollments.enroll_student(cursor, conn, course_id, payload.student_id)


@router.post("/courses/{course_id}/drop", response_model=EnrollmentOut)
async def drop(
    course_id: int,
    payload: EnrollmentCreate,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (1, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user['role_id'] == 1 and payload.student_id != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_enrollments.drop_course(cursor, conn, course_id, payload.student_id)


@router.get("/me/enrollments", response_model=List[EnrollmentWithCourse])
async def my_enrollments(
    student_id: int,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (1, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user['role_id'] == 1 and student_id != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_enrollments.list_student_enrollments(cursor, student_id)


@router.get("/courses/{course_id}/students", response_model=List[EnrollmentWithStudent])
async def course_students(
    course_id: int,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user['role_id'] == 2:
        course = await crud_course.get_course_by_id(cursor, course_id)
        if not course or course['teacher_id'] != current_user['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_enrollments.list_course_students(cursor, course_id)
