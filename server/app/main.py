from fastapi import FastAPI
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

from app.middleware.operation_log import OperationLogMiddleware

from app.db.session import engine, Base
from contextlib import asynccontextmanager

from app.db.session import engine, Base, SessionLocal
from app.models.role import Role
from sqlalchemy import select
from contextlib import asynccontextmanager

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

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(OperationLogMiddleware)

@app.get("/")
async def root():
    return {"message": "Welcome to USTC Database Learning Platform API"}

from app.routers import auth, users, courses, sections

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(courses.router, prefix=f"{settings.API_V1_STR}/courses", tags=["courses"])
app.include_router(sections.router, prefix=settings.API_V1_STR, tags=["sections"])  # No prefix because it has mixed paths

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
