from typing import AsyncGenerator, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from app.core.config import settings
from app.crud import crud_user
from app.db.mysql_pool import get_db_cursor
from app.schemas.token import TokenData

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    cursor_conn = Depends(get_db_cursor),
    token: str = Depends(reusable_oauth2)
) -> Dict[str, Any]:
    """获取当前用户（从JWT token）"""
    cursor, conn = cursor_conn
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = await crud_user.get_user_by_id(cursor, user_id=int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """确保当前用户是活跃的"""
    if not current_user.get('is_active', True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_roles(*role_ids: int):
    """要求特定角色权限的依赖"""
    async def _role_checker(
        current_user: Dict[str, Any] = Depends(get_current_active_user),
    ) -> Dict[str, Any]:
        if current_user.get('role_id') not in role_ids:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return _role_checker

def get_current_active_superuser(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取当前管理员用户（role_id = 3）"""
    if current_user.get('role_id') != 3:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

