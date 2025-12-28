from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Response, HTTPException, status
from app.crud import scores as crud_scores
from app.crud import crud_course
from app.db.mysql_pool import get_db_cursor
from app.routers import get_current_active_user
from app.schemas.scores import ScoreOut

router = APIRouter(tags=["Scores"])


@router.get("/me/scores", response_model=List[ScoreOut])
async def my_scores(
    student_id: int,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (1, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user['role_id'] == 1 and student_id != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_scores.get_scores_for_student(cursor, student_id)


@router.get("/courses/{course_id}/scores", response_model=List[ScoreOut])
async def course_scores(
    course_id: int,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user['role_id'] == 2:
        course = await crud_course.get_course_by_id(cursor, course_id)
        if not course or course['teacher_id'] != current_user['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return await crud_scores.get_scores_for_course(cursor, course_id)


@router.get("/courses/{course_id}/scores/export")
async def export_scores(
    course_id: int,
    cursor_conn = Depends(get_db_cursor),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
):
    cursor, conn = cursor_conn
    if current_user['role_id'] not in (2, 3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    if current_user['role_id'] == 2:
        course = await crud_course.get_course_by_id(cursor, course_id)
        if not course or course['teacher_id'] != current_user['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    csv_body = await crud_scores.export_scores_csv(cursor, course_id)
    return Response(content=csv_body, media_type="text/csv")
