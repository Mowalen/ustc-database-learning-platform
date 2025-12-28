from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers import get_current_active_user
from app.core import security
from app.core.password_reset import password_reset_store
from app.core.security import get_password_hash
from app.core.config import settings
from app.crud.crud_user import user as crud_user
from app.schemas.password_reset import (
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
)
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.db.session import get_db

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = await crud_user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserResponse)
async def register_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    user = await crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user = await crud_user.create(db, obj_in=user_in)
    return user


@router.post("/password-reset/request", response_model=PasswordResetResponse)
async def request_password_reset(
    payload: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    user = await crud_user.get_by_email(db, email=payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    code = password_reset_store.issue(payload.email)
    return PasswordResetResponse(message="Verification code generated", code=code)


@router.post("/password-reset/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(
    payload: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
) -> Any:
    user = await crud_user.get_by_email(db, email=payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    if not password_reset_store.verify(payload.email, payload.code):
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    user.password_hash = get_password_hash(payload.new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return PasswordResetResponse(message="Password updated")
