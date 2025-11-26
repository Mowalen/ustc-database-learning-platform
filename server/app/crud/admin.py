import hashlib

from fastapi import HTTPException, status
from sqlalchemy import select

from app import models
from app.schemas import AnnouncementCreate, UserCreate, UserUpdate


def _hash_password(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


async def _get_role(session, role_id: int) -> models.Role:
    role = await session.get(models.Role, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role_id")
    return role


async def create_user(session, payload: UserCreate) -> models.User:
    await _get_role(session, payload.role_id)

    stmt = select(models.User).where(models.User.username == payload.username)
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    user = models.User(
        username=payload.username,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        role_id=payload.role_id,
        avatar_url=payload.avatar_url,
        is_active=payload.is_active,
        password_hash=_hash_password(payload.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session, user_id: int, payload: UserUpdate) -> models.User:
    user = await session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.role_id is not None:
        await _get_role(session, payload.role_id)
        user.role_id = payload.role_id
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.email is not None:
        user.email = payload.email
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password:
        user.password_hash = _hash_password(payload.password)

    await session.commit()
    await session.refresh(user)
    return user


async def deactivate_user(session, user_id: int) -> models.User:
    user = await session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    await session.commit()
    await session.refresh(user)
    return user


async def deactivate_course(session, course_id: int) -> models.Course:
    course = await session.get(models.Course, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    course.is_active = False
    await session.commit()
    await session.refresh(course)
    return course


async def create_announcement(session, payload: AnnouncementCreate) -> models.Announcement:
    creator = await session.get(models.User, payload.created_by)
    if not creator:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Creator not found")

    announcement = models.Announcement(
        title=payload.title, content=payload.content, created_by=payload.created_by, is_active=payload.is_active
    )
    session.add(announcement)
    await session.commit()
    await session.refresh(announcement)
    return announcement


async def list_announcements(session, include_inactive: bool = False) -> list[models.Announcement]:
    stmt = select(models.Announcement)
    if not include_inactive:
        stmt = stmt.where(models.Announcement.is_active.is_(True))

    result = await session.execute(stmt.order_by(models.Announcement.created_at.desc()))
    return list(result.scalars().all())
