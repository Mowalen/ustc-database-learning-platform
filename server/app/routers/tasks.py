from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from app.crud import tasks as crud_tasks, crud_course
from app.db.mysql_pool import get_db_cursor
from app.routers import get_current_active_user
from app.schemas.submissions import GradeUpdate, SubmissionCreate, SubmissionOut, SubmissionWithStudent
from app.schemas.tasks import TaskCreate, TaskOut

router = APIRouter(tags=["Tasks"])


@router.post("/courses/{course_id}/tasks", response_model=TaskOut)
async def create_task(
    course_id: int,
    payload: TaskCreate,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user['role_id'] == 2 and payload.teacher_id != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher mismatch")
    
    # Verify course exists
    course = await crud_course.get_course_by_id(cursor, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        
    task_data = jsonable_encoder(payload)
    return await crud_tasks.create_task(cursor, conn, course_id, task_data)


@router.get("/courses/{course_id}/tasks", response_model=List[TaskOut])
async def list_tasks(
    course_id: int,
    cursor_conn = Depends(get_db_cursor)
):
    cursor, conn = cursor_conn
    return await crud_tasks.list_tasks(cursor, course_id)


@router.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int, 
    cursor_conn = Depends(get_db_cursor)
):
    cursor, conn = cursor_conn
    return await crud_tasks.get_task_by_id(cursor, task_id)


@router.post("/tasks/{task_id}/submit", response_model=SubmissionOut)
async def submit_task(
    task_id: int,
    payload: SubmissionCreate,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (1, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user['role_id'] == 1 and payload.student_id != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
    submission_data = jsonable_encoder(payload)
    return await crud_tasks.submit_task(cursor, conn, task_id, submission_data)


@router.put("/submissions/{submission_id}/grade", response_model=SubmissionOut)
async def grade_submission(
    submission_id: int,
    payload: GradeUpdate,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
    submission = await crud_tasks.get_submission_by_id(cursor, submission_id)
    
    # Check permissions logic
    if current_user['role_id'] == 2:
        # Need to check if teacher owns the course
        course_id = submission['task']['course_id']
        course = await crud_course.get_course_by_id(cursor, course_id)
        if not course or course['teacher_id'] != current_user['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
            
    grade_data = jsonable_encoder(payload)
    return await crud_tasks.apply_grade(cursor, conn, submission_id, grade_data)


@router.get("/tasks/{task_id}/submissions", response_model=List[SubmissionWithStudent])
async def list_submissions(
    task_id: int,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
    task = await crud_tasks.get_task_by_id(cursor, task_id)
    if current_user['role_id'] == 2:
        course = await crud_course.get_course_by_id(cursor, task['course_id'])
        if not course or course['teacher_id'] != current_user['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
            
    return await crud_tasks.list_submissions(cursor, task_id)
