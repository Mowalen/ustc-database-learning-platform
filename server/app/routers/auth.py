from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.routers import get_current_active_user
from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.db.mysql_pool import get_db_cursor
import aiomysql

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    cursor_conn = Depends(get_db_cursor),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    cursor, conn = cursor_conn
    
    user = await crud_user.authenticate_user(
        cursor, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.get('is_active', True):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user['id'], expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserResponse)
async def register_user(
    *,
    cursor_conn = Depends(get_db_cursor),
    user_in: UserCreate,
) -> Any:
    cursor, conn = cursor_conn
    
    user = await crud_user.get_user_by_username(cursor, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user = await crud_user.create_user(cursor, conn, user_in)
    return user

