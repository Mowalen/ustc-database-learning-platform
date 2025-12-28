from contextlib import asynccontextmanager
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.mysql_pool import mysql_pool
from app.middleware.operation_log import OperationLogMiddleware
from app.crud.crud_role import create_default_roles
import aiomysql

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 创建MySQL连接池
    await mysql_pool.create_pool()
    
    # 初始化默认角色
    async with mysql_pool.get_cursor() as (cursor, conn):
        created = await create_default_roles(cursor, conn)
        if created:
            print("Default roles created.")
    
    yield
    
    # 关闭MySQL连接池
    await mysql_pool.close_pool()

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)

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

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(courses.router, prefix=f"{settings.API_V1_STR}/courses", tags=["courses"])
app.include_router(sections.router, prefix=settings.API_V1_STR, tags=["sections"])
app.include_router(enrollments.router, prefix=settings.API_V1_STR, tags=["enrollments"])
app.include_router(tasks.router, prefix=settings.API_V1_STR, tags=["tasks"])
app.include_router(scores.router, prefix=settings.API_V1_STR, tags=["scores"])
app.include_router(admin_router.router, prefix=settings.API_V1_STR, tags=["admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
