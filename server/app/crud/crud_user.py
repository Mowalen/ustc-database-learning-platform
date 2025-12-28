"""
用户CRUD操作 - 使用原生MySQL
"""
from typing import Optional, List, Dict, Any
from app.db.query_helper import (
    build_insert_query,
    build_update_query,
    build_select_query,
    build_delete_query,
    fetch_one,
    fetch_all,
    execute_query,
    exclude_none_values
)
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_id(cursor, user_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取用户"""
    sql = """
        SELECT 
            u.id, u.username, u.password_hash, u.full_name, u.email, u.phone,
            u.role_id, u.avatar_url, u.is_active, u.created_at, u.updated_at,
            r.name as role_name, r.description as role_description
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE u.id = %s
    """
    await cursor.execute(sql, [user_id])
    result = await cursor.fetchone()
    
    if result:
        # 将role信息嵌套
        user = dict(result)
        user['role'] = {
            'id': user['role_id'],
            'name': user.get('role_name'),
            'description': user.get('role_description')
        }
        # 移除重复的role字段
        user.pop('role_name', None)
        user.pop('role_description', None)
    
    return result


async def get_user_by_username(cursor, username: str) -> Optional[Dict[str, Any]]:
    """根据用户名获取用户"""
    sql = """
        SELECT 
            u.id, u.username, u.password_hash, u.full_name, u.email, u.phone,
            u.role_id, u.avatar_url, u.is_active, u.created_at, u.updated_at,
            r.name as role_name, r.description as role_description
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE u.username = %s
    """
    await cursor.execute(sql, [username])
    result = await cursor.fetchone()
    
    if result:
        # 将role信息嵌套
        user = dict(result)
        user['role'] = {
            'id': user['role_id'],
            'name': user.get('role_name'),
            'description': user.get('role_description')
        }
        # 移除重复的role字段
        user.pop('role_name', None)
        user.pop('role_description', None)
    
    return result


async def get_users(
    cursor,
    skip: int = 0,
    limit: int = 100,
    role_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """获取用户列表"""
    sql = """
        SELECT 
            u.id, u.username, u.password_hash, u.full_name, u.email, u.phone,
            u.role_id, u.avatar_url, u.is_active, u.created_at, u.updated_at,
            r.name as role_name, r.description as role_description
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
    """
    params = []
    
    if role_id:
        sql += " WHERE u.role_id = %s"
        params.append(role_id)
    
    sql += f" ORDER BY u.created_at DESC LIMIT {limit} OFFSET {skip}"
    
    await cursor.execute(sql, params)
    results = await cursor.fetchall()
    
    users = []
    for result in results:
        user = dict(result)
        user['role'] = {
            'id': user['role_id'],
            'name': user.get('role_name'),
            'description': user.get('role_description')
        }
        user.pop('role_name', None)
        user.pop('role_description', None)
        users.append(user)
    
    return users


async def create_user(cursor, conn, user_in: UserCreate) -> Dict[str, Any]:
    """创建用户"""
    user_data = {
        'username': user_in.username,
        'password_hash': get_password_hash(user_in.password),
        'full_name': user_in.full_name,
        'email': user_in.email,
        'role_id': user_in.role_id,
        'is_active': user_in.is_active if hasattr(user_in, 'is_active') else True,
    }
    
    # 移除None值
    user_data = exclude_none_values(user_data)
    
    sql, params = build_insert_query('users', user_data)
    await cursor.execute(sql, params)
    await conn.commit()
    
    # 获取新创建的用户ID
    user_id = cursor.lastrowid
    
    # 返回创建的用户
    return await get_user_by_id(cursor, user_id)


async def update_user(
    cursor,
    conn,
    user_id: int,
    user_update: UserUpdate
) -> Optional[Dict[str, Any]]:
    """更新用户"""
    # 构建更新数据
    update_data = {}
    
    if user_update.username is not None:
        update_data['username'] = user_update.username
    if user_update.email is not None:
        update_data['email'] = user_update.email
    if user_update.full_name is not None:
        update_data['full_name'] = user_update.full_name
    if user_update.phone is not None:
        update_data['phone'] = user_update.phone
    if user_update.avatar_url is not None:
        update_data['avatar_url'] = user_update.avatar_url
    if user_update.is_active is not None:
        update_data['is_active'] = user_update.is_active
    if user_update.role_id is not None:
        update_data['role_id'] = user_update.role_id
    if hasattr(user_update, 'password') and user_update.password:
        update_data['password_hash'] = get_password_hash(user_update.password)
    
    if not update_data:
        # 没有要更新的数据，直接返回当前用户
        return await get_user_by_id(cursor, user_id)
    
    sql, params = build_update_query('users', update_data, {'id': user_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    # 返回更新后的用户
    return await get_user_by_id(cursor, user_id)


async def delete_user(cursor, conn, user_id: int) -> bool:
    """删除用户"""
    sql, params = build_delete_query('users', {'id': user_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    return cursor.rowcount > 0


async def authenticate_user(cursor, username: str, password: str) -> Optional[Dict[str, Any]]:
    """认证用户"""
    user = await get_user_by_username(cursor, username)
    if not user:
        return None
    if not verify_password(password, user['password_hash']):
        return None
    return user


async def get_user_count(cursor, role_id: Optional[int] = None) -> int:
    """获取用户总数"""
    sql = "SELECT COUNT(*) as count FROM users"
    params = []
    
    if role_id:
        sql += " WHERE role_id = %s"
        params.append(role_id)
    
    await cursor.execute(sql, params)
    result = await cursor.fetchone()
    return result['count'] if result else 0
