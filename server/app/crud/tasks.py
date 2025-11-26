from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app import models
from app.schemas import GradeUpdate, SubmissionCreate, TaskCreate


async def _get_course(session, course_id: int) -> models.Course:
    course = await session.get(models.Course, course_id)
    if not course or not course.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or inactive")
    return course


async def _get_student_enrollment(session, course_id: int, student_id: int) -> models.CourseEnrollment:
    stmt = select(models.CourseEnrollment).where(
        models.CourseEnrollment.course_id == course_id,
        models.CourseEnrollment.student_id == student_id,
        models.CourseEnrollment.status == models.EnrollmentStatus.ACTIVE,
    )
    result = await session.execute(stmt)
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled in course")
    return enrollment


async def create_task(session, course_id: int, payload: TaskCreate) -> models.Task:
    course = await _get_course(session, course_id)
    if course.teacher_id != payload.teacher_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teacher mismatch for course")

    task = models.Task(
        course_id=course_id,
        teacher_id=payload.teacher_id,
        title=payload.title,
        description=payload.description,
        type=payload.type,
        deadline=payload.deadline,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def list_tasks(session, course_id: int) -> list[models.Task]:
    await _get_course(session, course_id)
    stmt = select(models.Task).where(models.Task.course_id == course_id).order_by(models.Task.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_task(session, task_id: int) -> models.Task:
    stmt = select(models.Task).where(models.Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def submit_task(session, task_id: int, payload: SubmissionCreate) -> models.Submission:
    task = await get_task(session, task_id)
    await _get_student_enrollment(session, task.course_id, payload.student_id)

    now = datetime.now(timezone.utc)
    status_value = models.SubmissionStatus.SUBMITTED
    if task.deadline and now > task.deadline:
        status_value = models.SubmissionStatus.LATE

    stmt = select(models.Submission).where(
        models.Submission.task_id == task_id, models.Submission.student_id == payload.student_id
    )
    result = await session.execute(stmt)
    submission = result.scalar_one_or_none()

    if submission:
        submission.answer_text = payload.answer_text
        submission.file_url = payload.file_url
        submission.status = status_value
        submission.submitted_at = now
    else:
        submission = models.Submission(
            task_id=task_id,
            student_id=payload.student_id,
            answer_text=payload.answer_text,
            file_url=payload.file_url,
            status=status_value,
            submitted_at=now,
        )
        session.add(submission)

    await session.commit()
    await session.refresh(submission)
    return submission


async def grade_submission(session, submission_id: int, payload: GradeUpdate) -> models.Submission:
    stmt = select(models.Submission).options(joinedload(models.Submission.task)).where(
        models.Submission.id == submission_id
    )
    result = await session.execute(stmt)
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    submission.score = payload.score
    submission.feedback = payload.feedback
    submission.status = payload.status or models.SubmissionStatus.GRADED
    submission.graded_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(submission)
    return submission

