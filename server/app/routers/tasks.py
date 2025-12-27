from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tasks as crud_tasks
from app.db.session import get_db
from app.models import Course
from app.models.user import User
from app.routers import get_current_active_user
from app.schemas.submissions import GradeUpdate, SubmissionCreate, SubmissionOut, SubmissionWithStudent
from app.schemas.tasks import TaskCreate, TaskOut

router = APIRouter(tags=["Tasks"])


@router.post("/courses/{course_id}/tasks", response_model=TaskOut)
async def create_task(
    course_id: int,
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user.role_id == 2 and payload.teacher_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher mismatch")
    if current_user.role_id == 3:
        course = await db.get(Course, course_id)
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return await crud_tasks.create_task(db, course_id, payload)


@router.get("/courses/{course_id}/tasks", response_model=list[TaskOut])
async def list_tasks(course_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_tasks.list_tasks(db, course_id)


@router.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_tasks.get_task(db, task_id)


@router.post("/tasks/{task_id}/submit", response_model=SubmissionOut)
async def submit_task(
    task_id: int,
    payload: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (1, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user.role_id == 1 and payload.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_tasks.submit_task(db, task_id, payload)


@router.put("/submissions/{submission_id}/grade", response_model=SubmissionOut)
async def grade_submission(
    submission_id: int,
    payload: GradeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    submission = await crud_tasks.get_submission_with_course(db, submission_id)
    if current_user.role_id == 2 and submission.task.course.teacher_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_tasks.apply_grade(db, submission, payload)


@router.get("/tasks/{task_id}/submissions", response_model=list[SubmissionWithStudent])
async def list_submissions(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    task = await crud_tasks.get_task(db, task_id)
    course = await db.get(Course, task.course_id)
    if current_user.role_id == 2 and course and course.teacher_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_tasks.list_submissions(db, task_id)
