from fastapi import APIRouter, Depends, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import scores as crud_scores
from app.db.session import get_db
from app.models import Course
from app.models.user import User
from app.routers import get_current_active_user
from app.schemas.scores import ScoreOut

router = APIRouter(tags=["Scores"])


@router.get("/me/scores", response_model=list[ScoreOut])
async def my_scores(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (1, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user.role_id == 1 and student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_scores.get_scores_for_student(db, student_id)


@router.get("/teacher/pending-grading-count")
async def get_pending_grading_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id != 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a teacher")
    count = await crud_scores.get_teacher_pending_grading_count(db, current_user.id)
    return {"count": count}


@router.get("/student/pending-tasks-count")
async def get_student_pending_tasks_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a student")
        
    count = await crud_scores.get_student_pending_task_count(db, current_user.id)
    return {"count": count}


@router.get("/courses/{course_id}/scores", response_model=list[ScoreOut])
async def course_scores(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user.role_id == 2:
        course = await db.get(Course, course_id)
        if not course or course.teacher_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_scores.get_scores_for_course(db, course_id)


@router.get("/courses/{course_id}/scores/export")
async def export_scores(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role_id not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user.role_id == 2:
        course = await db.get(Course, course_id)
        if not course or course.teacher_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    csv_body = await crud_scores.export_scores_csv(db, course_id)
    return Response(content=csv_body, media_type="text/csv")
