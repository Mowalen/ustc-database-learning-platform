from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers import get_current_active_user
from app.core.security import verify_password, get_password_hash
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

@router.post("/verify-password")
async def verify_user_password(
    password: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not verify_password(password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return {"message": "Password verified"}

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    # Update full_name
    if full_name is not None:
        current_user.full_name = full_name
    
    # Update password (hash it first)
    if password is not None:
        current_user.password_hash = get_password_hash(password)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
