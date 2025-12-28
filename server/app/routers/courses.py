from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from app.routers import get_current_active_user, require_roles
from app.crud import crud_course, crud_category
from app.schemas.course import Course, CourseCreate, CourseUpdate, CourseCategory, CourseCategoryCreate
from app.db.mysql_pool import get_db_cursor

router = APIRouter()

@router.get("/", response_model=List[Course])
async def read_courses(
    cursor_conn = Depends(get_db_cursor),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    cursor, conn = cursor_conn
    return await crud_course.get_courses(cursor, skip=skip, limit=limit)

@router.post("/", response_model=Course)
async def create_course(
    *,
    cursor_conn = Depends(get_db_cursor),
    course_in: CourseCreate,
    current_user: Dict[str, Any] = Depends(require_roles(2, 3)),
) -> Any:
    cursor, conn = cursor_conn
    
    # 手动设置 teacher_id
    course_data = jsonable_encoder(course_in)
    course_data["teacher_id"] = current_user['id']
    
    course = await crud_course.create_course(cursor, conn, course_data)
    return course

@router.get("/{id}", response_model=Course)
async def read_course(
    *,
    cursor_conn = Depends(get_db_cursor),
    id: int,
) -> Any:
    cursor, conn = cursor_conn
    course = await crud_course.get_course_by_id(cursor, id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{id}", response_model=Course)
async def update_course(
    *,
    cursor_conn = Depends(get_db_cursor),
    id: int,
    course_in: CourseUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Any:
    cursor, conn = cursor_conn
    course = await crud_course.get_course_by_id(cursor, id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # 检查权限：管理员(3)或该课程的老师
    if current_user['role_id'] != 3 and course['teacher_id'] != current_user['id']:
         raise HTTPException(status_code=403, detail="Not enough permissions")
         
    course_data = jsonable_encoder(course_in)
    course = await crud_course.update_course(cursor, conn, id, course_data)
    return course

@router.delete("/{id}", response_model=Course)
async def delete_course(
    *,
    cursor_conn = Depends(get_db_cursor),
    id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Any:
    cursor, conn = cursor_conn
    course = await crud_course.get_course_by_id(cursor, id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if current_user['role_id'] != 3 and course['teacher_id'] != current_user['id']:
         raise HTTPException(status_code=403, detail="Not enough permissions")
         
    await crud_course.delete_course(cursor, conn, id)
    return course

# Categories
@router.get("/categories/", response_model=List[CourseCategory])
async def read_categories(
    cursor_conn = Depends(get_db_cursor),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    cursor, conn = cursor_conn
    return await crud_category.get_categories(cursor, skip=skip, limit=limit)

@router.post("/categories/", response_model=CourseCategory)
async def create_category(
    *,
    cursor_conn = Depends(get_db_cursor),
    category_in: CourseCategoryCreate,
    current_user: Dict[str, Any] = Depends(require_roles(3)),
) -> Any:
    cursor, conn = cursor_conn
    category_data = jsonable_encoder(category_in)
    return await crud_category.create_category(cursor, conn, category_data)
