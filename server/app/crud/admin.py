"""
管理员CRUD操作 - 使用原生MySQL
"""
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from app.core.security import get_password_hash
from app.db.query_helper import build_update_query, exclude_none_values
from app.crud import crud_user, crud_role, crud_course, crud_announcement


async def _get_role(cursor, role_id: int) -> Dict[str, Any]:
    """获取角色（辅助函数）"""
    from app.crud.crud_role import get_role_by_id
    role = await get_role_by_id(cursor, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role_id")
    return role


async def create_user(cursor, conn, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """管理员创建用户"""
    await _get_role(cursor, user_data['role_id'])
    
    # 检查用户名是否已存在
    existing = await crud_user.get_user_by_username(cursor, user_data['username'])
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    # 创建用户
    from app.schemas.user import UserCreate
    user_create = UserCreate(**user_data)
    return await crud_user.create_user(cursor, conn, user_create)


async def update_user(cursor, conn, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """管理员更新用户"""
    # 检查用户是否存在
    user = await crud_user.get_user_by_id(cursor, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # 如果更新角色，验证角色是否存在
    if user_data.get('role_id'):
        await _get_role(cursor, user_data['role_id'])
    
    # 更新用户
    from app.schemas.user import UserUpdate
    user_update = UserUpdate(**user_data)
    return await crud_user.update_user(cursor, conn, user_id, user_update)


async def deactivate_user(cursor, conn, user_id: int) -> Dict[str, Any]:
    """停用用户"""
    user = await crud_user.get_user_by_id(cursor, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # 更新is_active为False
    sql, params = build_update_query('users', {'is_active': False}, {'id': user_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    return await crud_user.get_user_by_id(cursor, user_id)


async def deactivate_course(cursor, conn, course_id: int) -> Dict[str, Any]:
    """停用课程"""
    course = await crud_course.get_course_by_id(cursor, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    # 更新is_active为False
    sql, params = build_update_query('courses', {'is_active': False}, {'id': course_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    return await crud_course.get_course_by_id(cursor, course_id)


async def create_announcement(cursor, conn, announcement_data: Dict[str, Any]) -> Dict[str, Any]:
    """管理员创建公告"""
    # 检查创建者是否存在
    creator = await crud_user.get_user_by_id(cursor, announcement_data['created_by'])
    if not creator:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Creator not found")
    
    return await crud_announcement.create_announcement(cursor, conn, announcement_data)


async def list_announcements(cursor, include_inactive: bool = False) -> List[Dict[str, Any]]:
    """获取公告列表"""
    is_active = None if include_inactive else True
    return await crud_announcement.get_announcements(cursor, is_active=is_active)


async def list_users(
    cursor,
    skip: int = 0,
    limit: int = 100,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    """获取用户列表"""
    sql = """
        SELECT 
            u.id, u.username, u.full_name, u.email, u.phone,
            u.role_id, u.avatar_url, u.is_active, u.created_at, u.updated_at,
            r.name as role_name
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
    """
    
    where_clauses = []
    params = []
    
    if role_id is not None:
        where_clauses.append("u.role_id = %s")
        params.append(role_id)
    
    if is_active is not None:
        where_clauses.append("u.is_active = %s")
        params.append(is_active)
    
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    
    sql += f" ORDER BY u.id ASC LIMIT {limit} OFFSET {skip}"
    
    await cursor.execute(sql, params)
    results = await cursor.fetchall()
    
    users = []
    for result in results:
        user = dict(result)
        user['role'] = {
            'id': user['role_id'],
            'name': user.get('role_name')
        }
        user.pop('role_name', None)
        users.append(user)
    
    return users
