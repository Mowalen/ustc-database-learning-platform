from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers import get_current_active_user, require_roles
from app.crud.crud_user import user as crud_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.db.session import get_db

router = APIRouter()

@router.get("/search", response_model=List[UserResponse])
async def search_users(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(3)),
    limit: int = 10,
) -> Any:
    limit = min(max(limit, 1), 10)
    return await crud_user.search_users(db, query=q, limit=limit)

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: str = Body(None),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = await crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user
