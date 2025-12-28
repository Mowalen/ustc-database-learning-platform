from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from app.routers import get_current_active_user
from app.crud import crud_section, crud_course
from app.schemas.section import Section, SectionCreate, SectionUpdate
from app.db.mysql_pool import get_db_cursor

router = APIRouter()

@router.get("/courses/{course_id}/sections", response_model=List[Section])
async def read_course_sections(
    *,
    cursor_conn = Depends(get_db_cursor),
    course_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    cursor, conn = cursor_conn
    return await crud_section.get_sections_by_course(cursor, course_id=course_id, skip=skip, limit=limit)

@router.post("/courses/{course_id}/sections", response_model=Section)
async def create_section(
    *,
    cursor_conn = Depends(get_db_cursor),
    course_id: int,
    section_in: SectionCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Any:
    cursor, conn = cursor_conn
    course = await crud_course.get_course_by_id(cursor, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if current_user['role_id'] != 3 and course['teacher_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Ensure course_id matches if provided in schema
    if hasattr(section_in, 'course_id') and section_in.course_id != course_id:
         raise HTTPException(status_code=400, detail="Course ID mismatch")
    
    # 手动设置 course_id
    section_data = jsonable_encoder(section_in)
    section_data['course_id'] = course_id
    
    return await crud_section.create_section(cursor, conn, section_data)

@router.get("/sections/{id}", response_model=Section)
async def read_section(
    *,
    cursor_conn = Depends(get_db_cursor),
    id: int,
) -> Any:
    cursor, conn = cursor_conn
    section = await crud_section.get_section_by_id(cursor, id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section

@router.put("/sections/{id}", response_model=Section)
async def update_section(
    *,
    cursor_conn = Depends(get_db_cursor),
    id: int,
    section_in: SectionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Any:
    cursor, conn = cursor_conn
    section = await crud_section.get_section_by_id(cursor, id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    course = await crud_course.get_course_by_id(cursor, id=section['course_id'])
    if current_user['role_id'] != 3 and course['teacher_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    section_data = jsonable_encoder(section_in)
    section = await crud_section.update_section(cursor, conn, id, section_data)
    return section

@router.delete("/sections/{id}", response_model=Section)
async def delete_section(
    *,
    cursor_conn = Depends(get_db_cursor),
    id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Any:
    cursor, conn = cursor_conn
    section = await crud_section.get_section_by_id(cursor, id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    course = await crud_course.get_course_by_id(cursor, id=section['course_id'])
    if current_user['role_id'] != 3 and course['teacher_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    await crud_section.delete_section(cursor, conn, id)
    return section
