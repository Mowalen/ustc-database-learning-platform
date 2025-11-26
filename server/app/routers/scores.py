from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import scores as crud_scores
from app.db.session import get_db
from app.schemas.scores import ScoreOut

router = APIRouter(tags=["Scores"])


@router.get("/me/scores", response_model=list[ScoreOut])
async def my_scores(student_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_scores.get_scores_for_student(db, student_id)


@router.get("/courses/{course_id}/scores", response_model=list[ScoreOut])
async def course_scores(course_id: int, db: AsyncSession = Depends(get_db)):
    return await crud_scores.get_scores_for_course(db, course_id)


@router.get("/courses/{course_id}/scores/export")
async def export_scores(course_id: int, db: AsyncSession = Depends(get_db)):
    csv_body = await crud_scores.export_scores_csv(db, course_id)
    return Response(content=csv_body, media_type="text/csv")
