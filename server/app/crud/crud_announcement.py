"""
公告CRUD操作 - 使用原生MySQL
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.db.query_helper import (
    build_insert_query,
    build_update_query,
    build_delete_query,
    exclude_none_values
)


async def get_announcement_by_id(cursor, announcement_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取公告"""
    sql = """
        SELECT 
            a.id, a.title, a.content, a.created_by, a.created_at, a.is_active,
            u.username as creator_username, u.full_name as creator_name
        FROM announcements a
        LEFT JOIN users u ON a.created_by = u.id
        WHERE a.id = %s
    """
    await cursor.execute(sql, [announcement_id])
    result = await cursor.fetchone()
    
    if result:
        announcement = dict(result)
        announcement['creator'] = {
            'id': announcement['created_by'],
            'username': announcement.get('creator_username'),
            'full_name': announcement.get('creator_name')
        }
        announcement.pop('creator_username', None)
        announcement.pop('creator_name', None)
    
    return result


async def get_announcements(
    cursor,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """获取公告列表"""
    sql = """
        SELECT 
            a.id, a.title, a.content, a.created_by, a.created_at, a.is_active,
            u.username as creator_username, u.full_name as creator_name
        FROM announcements a
        LEFT JOIN users u ON a.created_by = u.id
    """
    params = []
    
    if is_active is not None:
        sql += " WHERE a.is_active = %s"
        params.append(is_active)
    
    sql += f" ORDER BY a.created_at DESC LIMIT {limit} OFFSET {skip}"
    
    await cursor.execute(sql, params)
    results = await cursor.fetchall()
    
    announcements = []
    for result in results:
        announcement = dict(result)
        announcement['creator'] = {
            'id': announcement['created_by'],
            'username': announcement.get('creator_username'),
            'full_name': announcement.get('creator_name')
        }
        announcement.pop('creator_username', None)
        announcement.pop('creator_name', None)
        announcements.append(announcement)
    
    return announcements


async def create_announcement(cursor, conn, announcement_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建公告"""
    data = {
        'title': announcement_data['title'],
        'content': announcement_data.get('content'),
        'created_by': announcement_data['created_by'],
        'is_active': announcement_data.get('is_active', True)
    }
    
    data = exclude_none_values(data)
    sql, params = build_insert_query('announcements', data)
    await cursor.execute(sql, params)
    await conn.commit()
    
    announcement_id = cursor.lastrowid
    return await get_announcement_by_id(cursor, announcement_id)


async def update_announcement(
    cursor,
    conn,
    announcement_id: int,
    announcement_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """更新公告"""
    update_data = exclude_none_values(announcement_data)
    
    if not update_data:
        return await get_announcement_by_id(cursor, announcement_id)
    
    sql, params = build_update_query('announcements', update_data, {'id': announcement_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    return await get_announcement_by_id(cursor, announcement_id)


async def delete_announcement(cursor, conn, announcement_id: int) -> bool:
    """删除公告"""
    sql, params = build_delete_query('announcements', {'id': announcement_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    return cursor.rowcount > 0


async def get_announcement_count(cursor, is_active: Optional[bool] = None) -> int:
    """获取公告总数"""
    sql = "SELECT COUNT(*) as count FROM announcements"
    params = []
    
    if is_active is not None:
        sql += " WHERE is_active = %s"
        params.append(is_active)
    
    await cursor.execute(sql, params)
    result = await cursor.fetchone()
    return result['count'] if result else 0
