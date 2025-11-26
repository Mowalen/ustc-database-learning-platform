from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers import get_current_active_user
from app.crud.crud_section import section as crud_section
from app.crud.crud_course import course as crud_course
from app.schemas.section import Section, SectionCreate, SectionUpdate
from app.models.user import User
from app.db.session import get_db

router = APIRouter()

@router.get("/courses/{course_id}/sections", response_model=List[Section])
async def read_course_sections(
    *,
    db: AsyncSession = Depends(get_db),
    course_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return await crud_section.get_multi_by_course(db, course_id=course_id, skip=skip, limit=limit)

@router.post("/courses/{course_id}/sections", response_model=Section)
async def create_section(
    *,
    db: AsyncSession = Depends(get_db),
    course_id: int,
    section_in: SectionCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    course = await crud_course.get(db, id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Ensure course_id matches
    if section_in.course_id != course_id:
         raise HTTPException(status_code=400, detail="Course ID mismatch")

    return await crud_section.create(db, obj_in=section_in)

@router.get("/sections/{id}", response_model=Section)
async def read_section(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
) -> Any:
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section

@router.put("/sections/{id}", response_model=Section)
async def update_section(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    section_in: SectionUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    course = await crud_course.get(db, id=section.course_id)
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    section = await crud_section.update(db, db_obj=section, obj_in=section_in)
    return section

@router.delete("/sections/{id}", response_model=Section)
async def delete_section(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    section = await crud_section.get(db, id=id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
        
    course = await crud_course.get(db, id=section.course_id)
    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    section = await crud_section.remove(db, id=id)
    return section
