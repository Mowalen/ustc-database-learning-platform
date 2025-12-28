from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers import get_current_active_user
from app.core.security import verify_password
from app.crud.crud_user import user as crud_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.db.session import get_db

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    old_password: str = Body(...),
    password: str = Body(None),
    full_name: str = Body(None),
    email: str = Body(None),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")
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
