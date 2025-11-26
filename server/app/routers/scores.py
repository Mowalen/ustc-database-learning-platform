from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.crud import scores as crud_scores
from app.database import get_session

router = APIRouter(tags=["Scores"])


@router.get("/me/scores", response_model=list[schemas.ScoreOut])
async def my_scores(student_id: int, session: AsyncSession = Depends(get_session)):
    return await crud_scores.get_scores_for_student(session, student_id)


@router.get("/courses/{course_id}/scores", response_model=list[schemas.ScoreOut])
async def course_scores(course_id: int, session: AsyncSession = Depends(get_session)):
    return await crud_scores.get_scores_for_course(session, course_id)


@router.get("/courses/{course_id}/scores/export")
async def export_scores(course_id: int, session: AsyncSession = Depends(get_session)):
    csv_body = await crud_scores.export_scores_csv(session, course_id)
    return Response(content=csv_body, media_type="text/csv")

