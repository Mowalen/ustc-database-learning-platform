from datetime import datetime, timezone
from app.core.time_utils import get_now


from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import Course, CourseEnrollment, EnrollmentStatus, User


async def _get_course(session, course_id: int) -> Course:
    course = await session.get(Course, course_id)
    if not course or not course.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or inactive")
    return course


async def _get_student(session, student_id: int) -> User:
    student = await session.get(User, student_id)
    if not student or not student.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or inactive")
    return student


async def enroll_student(session, course_id: int, student_id: int) -> CourseEnrollment:
    await _get_course(session, course_id)
    await _get_student(session, student_id)

    stmt = select(CourseEnrollment).where(CourseEnrollment.course_id == course_id, CourseEnrollment.student_id == student_id)
    result = await session.execute(stmt)
    enrollment = result.scalar_one_or_none()

    if enrollment:
        if enrollment.status == EnrollmentStatus.DROPPED:
            enrollment.status = EnrollmentStatus.ACTIVE
            enrollment.enrolled_at = get_now()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled")
    else:
        enrollment = CourseEnrollment(
            course_id=course_id,
            student_id=student_id,
            status=EnrollmentStatus.ACTIVE,
            enrolled_at=get_now(),
        )
        session.add(enrollment)

    await session.commit()
    await session.refresh(enrollment)
    return enrollment


async def drop_course(session, course_id: int, student_id: int) -> CourseEnrollment:
    await _get_course(session, course_id)
    await _get_student(session, student_id)

    stmt = select(CourseEnrollment).where(CourseEnrollment.course_id == course_id, CourseEnrollment.student_id == student_id)
    result = await session.execute(stmt)
    enrollment = result.scalar_one_or_none()
    if not enrollment or enrollment.status == EnrollmentStatus.DROPPED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    enrollment.status = EnrollmentStatus.DROPPED
    await session.commit()
    await session.refresh(enrollment)
    return enrollment


async def list_student_enrollments(session, student_id: int) -> list[CourseEnrollment]:
    await _get_student(session, student_id)
    stmt = (
        select(CourseEnrollment)
        .options(
            joinedload(CourseEnrollment.course).joinedload(Course.teacher)
        )
        .where(
            CourseEnrollment.student_id == student_id,
            CourseEnrollment.status == EnrollmentStatus.ACTIVE,
        )
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_course_students(session, course_id: int) -> list[CourseEnrollment]:
    await _get_course(session, course_id)
    stmt = (
        select(CourseEnrollment)
        .options(joinedload(CourseEnrollment.student).joinedload(User.role))
        .where(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.status == EnrollmentStatus.ACTIVE,
        )
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
