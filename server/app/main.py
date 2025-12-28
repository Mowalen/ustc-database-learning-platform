from contextlib import asynccontextmanager
from pathlib import Path
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.core.config import settings
from app.db.session import Base, SessionLocal, engine
from app.middleware.operation_log import OperationLogMiddleware
from app.models.role import Role

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed roles
    async with SessionLocal() as session:
        result = await session.execute(select(Role))
        roles = result.scalars().all()
        if not roles:
            roles_to_create = [
                Role(id=1, name="student", description="Student role"),
                Role(id=2, name="teacher", description="Teacher role"),
                Role(id=3, name="admin", description="Admin role"),
            ]
            session.add_all(roles_to_create)
            await session.commit()
            print("Roles seeded.")
            
    yield

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.add_middleware(OperationLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to USTC Database Learning Platform API"}

from app.routers import auth, courses, sections, users
from app.routers import admin as admin_router
from app.routers import enrollments, scores, tasks
from app.routers import uploads as uploads_router

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(courses.router, prefix=f"{settings.API_V1_STR}/courses", tags=["courses"])
app.include_router(sections.router, prefix=settings.API_V1_STR, tags=["sections"])
app.include_router(enrollments.router, prefix=settings.API_V1_STR, tags=["enrollments"])
app.include_router(tasks.router, prefix=settings.API_V1_STR, tags=["tasks"])
app.include_router(scores.router, prefix=settings.API_V1_STR, tags=["scores"])
app.include_router(admin_router.router, prefix=settings.API_V1_STR, tags=["admin"])
app.include_router(uploads_router.router, prefix=settings.API_V1_STR, tags=["uploads"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
