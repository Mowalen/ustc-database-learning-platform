from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import Course, CourseEnrollment, EnrollmentStatus, Submission, SubmissionStatus, Task, TaskType, User
from app.schemas.submissions import GradeUpdate, SubmissionCreate
from app.schemas.tasks import TaskCreate


async def _get_course(session, course_id: int) -> Course:
    course = await session.get(Course, course_id)
    if not course or not course.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or inactive")
    return course


async def _get_student_enrollment(session, course_id: int, student_id: int) -> CourseEnrollment:
    stmt = select(CourseEnrollment).where(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == student_id,
        CourseEnrollment.status == EnrollmentStatus.ACTIVE,
    )
    result = await session.execute(stmt)
    enrollment = result.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled in course")
    return enrollment


async def create_task(session, course_id: int, payload: TaskCreate) -> Task:
    course = await _get_course(session, course_id)
    if course.teacher_id != payload.teacher_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teacher mismatch for course")

    task = Task(
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


async def list_tasks(session, course_id: int) -> list[Task]:
    await _get_course(session, course_id)
    stmt = select(Task).where(Task.course_id == course_id).order_by(Task.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_task(session, task_id: int) -> Task:
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def submit_task(session, task_id: int, payload: SubmissionCreate) -> Submission:
    task = await get_task(session, task_id)
    await _get_student_enrollment(session, task.course_id, payload.student_id)

    now = datetime.now(timezone.utc)
    deadline = task.deadline
    if deadline and deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    status_value = SubmissionStatus.SUBMITTED
    if deadline and now > deadline:
        status_value = SubmissionStatus.LATE

    stmt = select(Submission).where(Submission.task_id == task_id, Submission.student_id == payload.student_id)
    result = await session.execute(stmt)
    submission = result.scalar_one_or_none()

    if submission:
        submission.answer_text = payload.answer_text
        submission.file_url = payload.file_url
        submission.status = status_value
        submission.submitted_at = now
    else:
        submission = Submission(
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


async def get_submission_with_course(session, submission_id: int) -> Submission:
    stmt = (
        select(Submission)
        .options(joinedload(Submission.task).joinedload(Task.course))
        .where(Submission.id == submission_id)
    )
    result = await session.execute(stmt)
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return submission


async def apply_grade(session, submission: Submission, payload: GradeUpdate) -> Submission:
    submission.score = payload.score
    submission.feedback = payload.feedback
    submission.status = payload.status or SubmissionStatus.GRADED
    submission.graded_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(submission)
    return submission


async def list_submissions(session, task_id: int) -> list[Submission]:
    stmt = (
        select(Submission)
        .options(joinedload(Submission.student).joinedload(User.role))
        .where(Submission.task_id == task_id)
        .order_by(Submission.submitted_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_task(session, task_id: int, payload) -> Task:
    task = await get_task(session, task_id)
    
    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.type is not None:
        task.type = payload.type
    if payload.deadline is not None:
        task.deadline = payload.deadline
    
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session, task_id: int) -> Task:
    task = await get_task(session, task_id)
    await session.delete(task)
    await session.commit()
    return task
