from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app import models


async def _get_course(session, course_id: int) -> models.Course:
    course = await session.get(models.Course, course_id)
    if not course or not course.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or inactive")
    return course


async def _get_student(session, student_id: int) -> models.User:
    student = await session.get(models.User, student_id)
    if not student or not student.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or inactive")
    return student


async def enroll_student(session, course_id: int, student_id: int) -> models.CourseEnrollment:
    await _get_course(session, course_id)
    await _get_student(session, student_id)

    stmt = select(models.CourseEnrollment).where(
        models.CourseEnrollment.course_id == course_id, models.CourseEnrollment.student_id == student_id
    )
    result = await session.execute(stmt)
    enrollment = result.scalar_one_or_none()

    if enrollment:
        if enrollment.status == models.EnrollmentStatus.DROPPED:
            enrollment.status = models.EnrollmentStatus.ACTIVE
            enrollment.enrolled_at = datetime.now(timezone.utc)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled")
    else:
        enrollment = models.CourseEnrollment(
            course_id=course_id,
            student_id=student_id,
            status=models.EnrollmentStatus.ACTIVE,
            enrolled_at=datetime.now(timezone.utc),
        )
        session.add(enrollment)

    await session.commit()
    await session.refresh(enrollment)
    return enrollment


async def drop_course(session, course_id: int, student_id: int) -> models.CourseEnrollment:
    await _get_course(session, course_id)
    await _get_student(session, student_id)

    stmt = select(models.CourseEnrollment).where(
        models.CourseEnrollment.course_id == course_id, models.CourseEnrollment.student_id == student_id
    )
    result = await session.execute(stmt)
    enrollment = result.scalar_one_or_none()
    if not enrollment or enrollment.status == models.EnrollmentStatus.DROPPED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    enrollment.status = models.EnrollmentStatus.DROPPED
    await session.commit()
    await session.refresh(enrollment)
    return enrollment


async def list_student_enrollments(session, student_id: int) -> list[models.CourseEnrollment]:
    await _get_student(session, student_id)
    stmt = (
        select(models.CourseEnrollment)
        .options(joinedload(models.CourseEnrollment.course))
        .where(
            models.CourseEnrollment.student_id == student_id,
            models.CourseEnrollment.status == models.EnrollmentStatus.ACTIVE,
        )
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_course_students(session, course_id: int) -> list[models.CourseEnrollment]:
    await _get_course(session, course_id)
    stmt = (
        select(models.CourseEnrollment)
        .options(joinedload(models.CourseEnrollment.student).joinedload(models.User.role))
        .where(
            models.CourseEnrollment.course_id == course_id,
            models.CourseEnrollment.status == models.EnrollmentStatus.ACTIVE,
        )
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
