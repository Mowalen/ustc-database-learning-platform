from typing import Any, Dict, Optional, Union, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, func, or_
from sqlalchemy.future import select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.username == username))
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
        return db_obj

    async def authenticate(self, db: AsyncSession, *, username: str, password: str) -> Optional[User]:
        user = await self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def search_users(
        self,
        db: AsyncSession,
        *,
        query: str,
        limit: int = 10,
    ) -> List[User]:
        query = query.strip()
        if not query:
            return []

        query_lower = query.lower()
        pattern = f"%{query_lower}%"
        username_lower = func.lower(User.username)
        full_name_lower = func.lower(func.coalesce(User.full_name, ""))
        email_lower = func.lower(func.coalesce(User.email, ""))
        phone_text = func.coalesce(User.phone, "")

        match_rank = case(
            (username_lower == query_lower, 0),
            (username_lower.like(f"{query_lower}%"), 1),
            (username_lower.like(pattern), 2),
            (full_name_lower.like(pattern), 3),
            (email_lower.like(pattern), 4),
            (phone_text.like(f"%{query}%"), 5),
            else_=6,
        )

        stmt = (
            select(User)
            .where(
                or_(
                    username_lower.like(pattern),
                    full_name_lower.like(pattern),
                    email_lower.like(pattern),
                    phone_text.like(f"%{query}%"),
                )
            )
            .order_by(match_rank, User.id)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

user = CRUDUser(User)
