"""
课程章节CRUD操作 - 使用原生MySQL
"""
from typing import Optional, List, Dict, Any
from app.db.query_helper import (
    build_insert_query,
    build_update_query,
    build_delete_query,
    exclude_none_values
)


async def get_section_by_id(cursor, section_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取章节"""
    sql = """
        SELECT 
            s.id, s.course_id, s.title, s.content, s.material_url,
            s.video_url, s.order_index, s.created_at, s.updated_at,
            c.title as course_title
        FROM course_sections s
        LEFT JOIN courses c ON s.course_id = c.id
        WHERE s.id = %s
    """
    await cursor.execute(sql, [section_id])
    result = await cursor.fetchone()
    
    if result:
        section = dict(result)
        section['course'] = {
            'id': section['course_id'],
            'title': section.get('course_title')
        } if section['course_id'] else None
        section.pop('course_title', None)
    
    return result


async def get_sections_by_course(
    cursor,
    course_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """根据课程ID获取章节列表"""
    sql = """
        SELECT 
            id, course_id, title, content, material_url,
            video_url, order_index, created_at, updated_at
        FROM course_sections
        WHERE course_id = %s
        ORDER BY order_index ASC
        LIMIT %s OFFSET %s
    """
    await cursor.execute(sql, [course_id, limit, skip])
    return await cursor.fetchall()


async def create_section(cursor, conn, section_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建章节"""
    section_data = exclude_none_values(section_data)
    
    sql, params = build_insert_query('course_sections', section_data)
    await cursor.execute(sql, params)
    await conn.commit()
    
    section_id = cursor.lastrowid
    return await get_section_by_id(cursor, section_id)


async def update_section(
    cursor,
    conn,
    section_id: int,
    section_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """更新章节"""
    update_data = exclude_none_values(section_data)
    
    if not update_data:
        return await get_section_by_id(cursor, section_id)
    
    sql, params = build_update_query('course_sections', update_data, {'id': section_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    return await get_section_by_id(cursor, section_id)


async def delete_section(cursor, conn, section_id: int) -> bool:
    """删除章节"""
    sql, params = build_delete_query('course_sections', {'id': section_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    return cursor.rowcount > 0


async def get_section_count(cursor, course_id: int) -> int:
    """获取课程的章节总数"""
    sql = "SELECT COUNT(*) as count FROM course_sections WHERE course_id = %s"
    await cursor.execute(sql, [course_id])
    result = await cursor.fetchone()
    return result['count'] if result else 0
