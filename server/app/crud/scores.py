import csv
import io
from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy import select, func
from app.models import Submission, Task, Course, SubmissionStatus

async def get_teacher_pending_grading_count(session, teacher_id: int) -> int:
    stmt = (
        select(func.count(Submission.id))
        .join(Task, Submission.task_id == Task.id)
        .join(Course, Task.course_id == Course.id)
        .where(Course.teacher_id == teacher_id)
        .where(Submission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.LATE]))
    )
    result = await session.execute(stmt)
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
