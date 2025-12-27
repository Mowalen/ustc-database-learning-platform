from fastapi import HTTPException, status
from sqlalchemy import select

from app.core.security import get_password_hash
from app.models import Announcement, Course, Role, User
from app.schemas.announcements import AnnouncementCreate
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
    
    # 重新查询以加载关系
    from sqlalchemy.orm import selectinload
    result = await session.execute(
        select(User)
        .options(selectinload(User.role))
        .filter(User.id == user.id)
    )
    return result.scalars().first()


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
    
    # 重新查询以加载关系
    from sqlalchemy.orm import selectinload
    result = await session.execute(
        select(User)
        .options(selectinload(User.role))
        .filter(User.id == user.id)
    )
    return result.scalars().first()


async def deactivate_user(session, user_id: int) -> User:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    await session.commit()
    await session.refresh(user)
    
    # 重新查询以加载关系
    from sqlalchemy.orm import selectinload
    result = await session.execute(
        select(User)
        .options(selectinload(User.role))
        .filter(User.id == user.id)
    )
    return result.scalars().first()


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


async def list_users(session, role_id: int | None = None, include_inactive: bool = False, skip: int = 0, limit: int = 100) -> list[User]:
    """
    获取用户列表
    
    Args:
        session: 数据库会话
        role_id: 按角色筛选（可选）
        include_inactive: 是否包含已停用用户
        skip: 分页偏移量
        limit: 分页限制
    
    Returns:
        用户列表
    """
    stmt = select(User).options(selectinload(User.role))
    
    if role_id is not None:
        stmt = stmt.where(User.role_id == role_id)
    
    if not include_inactive:
        stmt = stmt.where(User.is_active.is_(True))
    
    stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def list_all_courses(session, include_inactive: bool = False, skip: int = 0, limit: int = 100) -> list[Course]:
    """
    获取所有课程列表（管理员视图）
    
    Args:
        session: 数据库会话
        include_inactive: 是否包含已下架课程
        skip: 分页偏移量
        limit: 分页限制
    
    Returns:
        课程列表
    """
    stmt = select(Course)
    
    if not include_inactive:
        stmt = stmt.where(Course.is_active.is_(True))
    
    stmt = stmt.order_by(Course.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())
