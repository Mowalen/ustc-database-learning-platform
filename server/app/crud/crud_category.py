"""
课程分类CRUD操作 - 使用原生MySQL
"""
from typing import Optional, List, Dict, Any
from app.db.query_helper import (
    build_insert_query,
    build_update_query,
    build_delete_query,
    exclude_none_values
)

async def get_category_by_id(cursor, category_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取分类"""
    sql = "SELECT id, name, description, created_at, updated_at FROM course_categories WHERE id = %s"
    await cursor.execute(sql, [category_id])
    return await cursor.fetchone()

async def get_categories(
    cursor,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """获取分类列表"""
    sql = "SELECT id, name, description, created_at, updated_at FROM course_categories ORDER BY id LIMIT %s OFFSET %s"
    await cursor.execute(sql, [limit, skip])
    return await cursor.fetchall()

async def create_category(cursor, conn, category_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建分类"""
    category_data = exclude_none_values(category_data)
    sql, params = build_insert_query('course_categories', category_data)
    await cursor.execute(sql, params)
    await conn.commit()
    
    category_id = cursor.lastrowid
    return await get_category_by_id(cursor, category_id)

async def update_category(
    cursor,
    conn,
    category_id: int,
    category_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """更新分类"""
    update_data = exclude_none_values(category_data)
    if not update_data:
        return await get_category_by_id(cursor, category_id)
        
    sql, params = build_update_query('course_categories', update_data, {'id': category_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    return await get_category_by_id(cursor, category_id)

async def delete_category(cursor, conn, category_id: int) -> bool:
    """删除分类"""
    sql, params = build_delete_query('course_categories', {'id': category_id})
    await cursor.execute(sql, params)
    await conn.commit()
    return cursor.rowcount > 0
