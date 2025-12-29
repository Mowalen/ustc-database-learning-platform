import csv
import io
from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy import select, func
from app.models import Submission, Task, Course, SubmissionStatus, CourseEnrollment, EnrollmentStatus

async def get_teacher_pending_grading_count(session, teacher_id: int) -> int:
    stmt = (
        select(func.count(Submission.id))
        .join(Task, Submission.task_id == Task.id)
        .join(Course, Task.course_id == Course.id)
        .join(CourseEnrollment, (CourseEnrollment.course_id == Course.id) & (CourseEnrollment.student_id == Submission.student_id))
        .where(Course.teacher_id == teacher_id)
        .where(Submission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.LATE]))
        .where(CourseEnrollment.status == EnrollmentStatus.ACTIVE)
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_student_pending_task_count(session, student_id: int) -> int:
    # 1. Get active enrolled course IDs
    from app.models import CourseEnrollment, EnrollmentStatus
    stmt_courses = select(CourseEnrollment.course_id).where(
        CourseEnrollment.student_id == student_id,
        CourseEnrollment.status == EnrollmentStatus.ACTIVE
    )
    result_courses = await session.execute(stmt_courses)
    course_ids = result_courses.scalars().all()

    if not course_ids:
        return 0

    # 2. Get submitted task IDs
    stmt_submissions = select(Submission.task_id).where(Submission.student_id == student_id)
    result_submissions = await session.execute(stmt_submissions)
    submitted_task_ids = set(result_submissions.scalars().all())

    # 3. Count tasks in these courses that are NOT in submitted_task_ids
    # Note: We can do this in one complex SQL query, but this is readable and reasonably efficient for typical sizes.
    # SQL way:
    # SELECT count(*) FROM tasks 
    # WHERE course_id IN (...) 
    # AND id NOT IN (SELECT task_id FROM submissions WHERE student_id = ...)
    
    stmt_count = (
        select(func.count(Task.id))
        .where(Task.course_id.in_(course_ids))
    )
    
    if submitted_task_ids:
        stmt_count = stmt_count.where(Task.id.not_in(submitted_task_ids))
        
    result = await session.execute(stmt_count)
    return result.scalar_one()



async def get_scores_for_student(session, student_id: int) -> list[dict]:
    stmt = (
        select(Submission, Task)
        .join(Task, Submission.task_id == Task.id)
        .where(Submission.student_id == student_id)
    )
    result = await session.execute(stmt)
    rows = result.all()
    if not rows:
        return []

    scores = []
    for submission, task in rows:
        scores.append(
            {
                "submission_id": submission.id,
                "course_id": task.course_id,
                "task_id": task.id,
                "task_title": task.title,
                "student_id": submission.student_id,
                "score": submission.score,
                "feedback": submission.feedback,
                "status": submission.status,
                "graded_at": submission.graded_at,
            }
        )
    return scores


async def get_scores_for_course(session, course_id: int) -> list[dict]:
    stmt = (
        select(Submission, Task)
        .join(Task, Submission.task_id == Task.id)
        .where(Task.course_id == course_id)
    )
    result = await session.execute(stmt)
    rows = result.all()
    if not rows:
        return []

    scores = []
    for submission, task in rows:
        scores.append(
            {
                "submission_id": submission.id,
                "course_id": task.course_id,
                "task_id": task.id,
                "task_title": task.title,
                "student_id": submission.student_id,
                "score": submission.score,
                "feedback": submission.feedback,
                "status": submission.status,
                "graded_at": submission.graded_at,
            }
        )
    return scores


async def export_scores_csv(session, course_id: int) -> str:
    scores = await get_scores_for_course(session, course_id)
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["submission_id", "course_id", "task_id", "task_title", "student_id", "score", "status", "graded_at"],
    )
    writer.writeheader()
    writer.writerows(_coerce_to_strings(scores))
    return output.getvalue()


def _coerce_to_strings(rows: Iterable[dict]) -> Iterable[dict]:
    for row in rows:
        yield {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
