from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.crud import tasks as crud_tasks
from app.database import get_session

router = APIRouter(tags=["Tasks"])


@router.post("/courses/{course_id}/tasks", response_model=schemas.TaskOut)
async def create_task(
    course_id: int, payload: schemas.TaskCreate, session: AsyncSession = Depends(get_session)
):
    return await crud_tasks.create_task(session, course_id, payload)


@router.get("/courses/{course_id}/tasks", response_model=list[schemas.TaskOut])
async def list_tasks(course_id: int, session: AsyncSession = Depends(get_session)):
    return await crud_tasks.list_tasks(session, course_id)


@router.get("/tasks/{task_id}", response_model=schemas.TaskOut)
async def get_task(task_id: int, session: AsyncSession = Depends(get_session)):
    return await crud_tasks.get_task(session, task_id)


@router.post("/tasks/{task_id}/submit", response_model=schemas.SubmissionOut)
async def submit_task(task_id: int, payload: schemas.SubmissionCreate, session: AsyncSession = Depends(get_session)):
    return await crud_tasks.submit_task(session, task_id, payload)


@router.put("/submissions/{submission_id}/grade", response_model=schemas.SubmissionOut)
async def grade_submission(
    submission_id: int, payload: schemas.GradeUpdate, session: AsyncSession = Depends(get_session)
):
    return await crud_tasks.grade_submission(session, submission_id, payload)

