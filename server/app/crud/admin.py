from fastapi import HTTPException, status
from sqlalchemy import select

from app.core.security import get_password_hash
from app.models import Announcement, Course, Role, User
from app.schemas.announcements import AnnouncementCreate, AnnouncementUpdate
from app.schemas.user import UserCreate, UserUpdate


async def _get_role(session, role_id: int) -> Role:
    role = await session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role_id")
    return role


async def create_user(session, payload: UserCreate) -> User:
    await _get_role(session, payload.role_id)

    stmt = select(User).where(User.username == payload.username)
    existing = (await session.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    user = User(
        username=payload.username,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        role_id=payload.role_id,
        avatar_url=payload.avatar_url,
        is_active=payload.is_active,
        password_hash=get_password_hash(payload.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session, user_id: int, payload: UserUpdate) -> User:
    user = await session.get(User, user_id)
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
        user.password_hash = get_password_hash(payload.password)

    await session.commit()
    await session.refresh(user)
    return user


async def deactivate_user(session, user_id: int) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    await session.commit()
    await session.refresh(user)
    return user


async def deactivate_course(session, course_id: int) -> Course:
    course = await session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    course.is_active = False
    await session.commit()
    await session.refresh(course)
    return course


async def create_announcement(session, payload: AnnouncementCreate) -> Announcement:
    creator = await session.get(User, payload.created_by)
    if not creator:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Creator not found")

    announcement = Announcement(
        title=payload.title, content=payload.content, created_by=payload.created_by, is_active=payload.is_active
    )
    session.add(announcement)
    await session.commit()
    await session.refresh(announcement)
    return announcement


async def list_announcements(session, include_inactive: bool = False) -> list[Announcement]:
    stmt = select(Announcement)
    if not include_inactive:
        stmt = stmt.where(Announcement.is_active.is_(True))

    result = await session.execute(stmt.order_by(Announcement.created_at.desc()))
    return list(result.scalars().all())


async def list_users(
    session,
    skip: int = 0,
    limit: int = 100,
    role_id: int | None = None,
    is_active: bool | None = None,
) -> list[User]:
    stmt = select(User).order_by(User.id.asc()).offset(skip).limit(limit)
    if role_id is not None:
        stmt = stmt.where(User.role_id == role_id)
    if is_active is not None:
        stmt = stmt.where(User.is_active.is_(is_active))
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_announcement(session, announcement_id: int, payload: AnnouncementUpdate) -> Announcement:
    announcement = await session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")

    if payload.title is not None:
        announcement.title = payload.title
    if payload.content is not None:
        announcement.content = payload.content
    if payload.is_active is not None:
        announcement.is_active = payload.is_active

    await session.commit()
    await session.refresh(announcement)
    return announcement


async def delete_announcement(session, announcement_id: int) -> Announcement:
    # We can choose to soft delete (deactivate) or hard delete.
    # Given other entities use deactivate, we can stick to that, or simple hard delete if less critical.
    # For now, let's reuse "is_active=False" conceptually as delete for user view, but admin might want hard delete.
    # User request was "delete" (usually), and previous code showed "include_inactive".
    # Let's support hard delete since announcements are simple, OR soft delete.
    # The previous code in list_announcements handles include_inactive.
    # So we probably should have deactivate. But "delete" is what is asked usually.
    # Let's do HARD delete for announcements to keep it clean, or just deactivate?
    # Actually, announcements are often ephemeral.
    # Let's do soft delete first (deactivate) to matching pattern.
    announcement = await session.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")

    # Hard delete example:
    # await session.delete(announcement)
    # await session.commit()
    # return announcement

    # Soft delete:
    announcement.is_active = False
    await session.commit()
    await session.refresh(announcement)
    return announcement
