from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from app.routers import get_current_active_user
from app.crud import crud_user
from app.schemas.user import UserResponse, UserUpdate
from app.db.mysql_pool import get_db_cursor

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Any:
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    *,
    cursor_conn = Depends(get_db_cursor),
    password: str = Body(None),
    full_name: str = Body(None),
    email: str = Body(None),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Any:
    cursor, conn = cursor_conn
    
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    
    user = await crud_user.update_user(cursor, conn, user_id=current_user['id'], user_update=user_in)
    return user
