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
    """
    请求密码重置 - 发送验证码到用户邮箱
    
    开发模式（DEV_MODE=True）：直接返回验证码，不发送邮件
    生产模式（DEV_MODE=False）：发送邮件到用户邮箱
    """
    user = await crud_user.get_by_email(db, email=payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # 生成验证码
    code = password_reset_store.issue(payload.email)
    
    # 根据模式决定是否发送邮件
    if settings.DEV_MODE:
        # 开发模式：直接返回验证码（方便测试）
        return PasswordResetResponse(
            message="Development mode: Verification code generated (not sent via email)",
            code=code
        )
    else:
        # 生产模式：发送邮件
        from app.core.email import email_service
        success = email_service.send_verification_code(
            to_email=payload.email,
            code=code,
            purpose="密码重置"
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send verification email. Please try again later."
            )
        
        return PasswordResetResponse(
            message="Verification code sent to your email"
        )


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
