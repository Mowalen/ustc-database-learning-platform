from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, courses, sections

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(sections.router, tags=["sections"]) # No prefix because it has mixed paths
