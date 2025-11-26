from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import tasks as crud_tasks
from app.db.session import get_db
from app.schemas.submissions import GradeUpdate, SubmissionCreate, SubmissionOut
from app.schemas.tasks import TaskCreate, TaskOut

router = APIRouter(tags=["Tasks"])


@router.post("/courses/{course_id}/tasks", response_model=TaskOut)
async def create_task(course_id: int, payload: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await crud_tasks.create_task(db, course_id, payload)


@router.get("/courses/{course_id}/tasks", response_model=list[TaskOut])
async def list_tasks(course_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_tasks.list_tasks(db, course_id)


@router.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_tasks.get_task(db, task_id)


@router.post("/tasks/{task_id}/submit", response_model=SubmissionOut)
async def submit_task(task_id: int, payload: SubmissionCreate, db: AsyncSession = Depends(get_db)):
    return await crud_tasks.submit_task(db, task_id, payload)


@router.put("/submissions/{submission_id}/grade", response_model=SubmissionOut)
async def grade_submission(submission_id: int, payload: GradeUpdate, db: AsyncSession = Depends(get_db)):
    return await crud_tasks.grade_submission(db, submission_id, payload)
