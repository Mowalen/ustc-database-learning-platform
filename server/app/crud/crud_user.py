from typing import Any, Dict, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .filter(User.username == username)
        )
        return result.scalars().first()

    async def get(self, db: AsyncSession, id: Any) -> Optional[User]:
        """覆盖基类的get方法，添加role预加载"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .filter(User.id == id)
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            full_name=obj_in.full_name,
            password_hash=get_password_hash(obj_in.password),
            role_id=obj_in.role_id,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # 重新查询以加载关系
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .filter(User.id == db_obj.id)
        )
        return result.scalars().first()

    async def authenticate(self, db: AsyncSession, *, username: str, password: str) -> Optional[User]:
        user = await self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    async def update(self, db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        """覆盖基类的update方法，添加role预加载"""
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                # 特殊处理密码
                if field == "password" and update_data[field]:
                    db_obj.password_hash = get_password_hash(update_data[field])
                else:
                    setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # 重新查询以加载关系
        result = await db.execute(
            select(User)
            .options(selectinload(User.role))
            .filter(User.id == db_obj.id)
        )
        return result.scalars().first()

user = CRUDUser(User)

