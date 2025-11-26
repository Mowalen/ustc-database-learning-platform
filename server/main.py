from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.database import get_session, lifespan
from app.routers import admin, enrollments, scores, tasks

app = FastAPI(lifespan=lifespan)

app.include_router(enrollments.router)
app.include_router(tasks.router)
app.include_router(scores.router)
app.include_router(admin.router)


@app.get("/healthz")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/roles")
async def list_roles(session: AsyncSession = Depends(get_session)):
    """Example query to verify tables are created and reachable."""
    result = await session.execute(select(models.Role))
    return [
        {"id": role.id, "name": role.name.value, "description": role.description}
        for role in result.scalars()
    ]


# For manual debugging: `uv run uvicorn main:app --reload`
