"""
课程CRUD操作 - 使用原生MySQL
"""
from typing import Optional, List, Dict, Any
from app.db.query_helper import (
    build_insert_query,
    build_update_query,
    build_delete_query,
    exclude_none_values
)


async def get_course_by_id(cursor, course_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取课程"""
    sql = """
        SELECT 
            c.id, c.teacher_id, c.title, c.description, c.cover_url,
            c.material_url, c.video_url, c.category_id, c.created_at,
            c.updated_at, c.is_active,
            u.username as teacher_username, u.full_name as teacher_name,
            cc.name as category_name, cc.description as category_description,
            cc.created_at as category_created_at, cc.updated_at as category_updated_at
        FROM courses c
        LEFT JOIN users u ON c.teacher_id = u.id
        LEFT JOIN course_categories cc ON c.category_id = cc.id
        WHERE c.id = %s
    """
    await cursor.execute(sql, [course_id])
    result = await cursor.fetchone()
    
    if result:
        course = dict(result)
        # 嵌套teacher信息
        course['teacher'] = {
            'id': course['teacher_id'],
            'username': course.get('teacher_username'),
            'full_name': course.get('teacher_name')
        } if course['teacher_id'] else None
        
        # 嵌套category信息
        course['category'] = {
            'id': course['category_id'],
            'name': course.get('category_name'),
            'description': course.get('category_description'),
            'created_at': course.get('category_created_at'),
            'updated_at': course.get('category_updated_at')
        } if course['category_id'] else None
        
        # 移除重复字段
        course.pop('teacher_username', None)
        course.pop('teacher_name', None)
        course.pop('category_name', None)
        course.pop('category_description', None)
        course.pop('category_created_at', None)
        course.pop('category_updated_at', None)
        
    return result


async def get_courses(
    cursor,
    skip: int = 0,
    limit: int = 100,
    teacher_id: Optional[int] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[Dict[str, Any]]:
    """获取课程列表"""
    sql = """
        SELECT 
            c.id, c.teacher_id, c.title, c.description, c.cover_url,
            c.material_url, c.video_url, c.category_id, c.created_at,
            c.updated_at, c.is_active,
            u.username as teacher_username, u.full_name as teacher_name,
            cc.name as category_name, cc.description as category_description,
            cc.created_at as category_created_at, cc.updated_at as category_updated_at
        FROM courses c
        LEFT JOIN users u ON c.teacher_id = u.id
        LEFT JOIN course_categories cc ON c.category_id = cc.id
    """
    
    where_clauses = []
    params = []
    
    if teacher_id is not None:
        where_clauses.append("c.teacher_id = %s")
        params.append(teacher_id)
    
    if category_id is not None:
        where_clauses.append("c.category_id = %s")
        params.append(category_id)
    
    if is_active is not None:
        where_clauses.append("c.is_active = %s")
        params.append(is_active)
    
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    
    sql += f" ORDER BY c.created_at DESC LIMIT {limit} OFFSET {skip}"
    
    await cursor.execute(sql, params)
    results = await cursor.fetchall()
    
    courses = []
    for result in results:
        course = dict(result)
        course['teacher'] = {
            'id': course['teacher_id'],
            'username': course.get('teacher_username'),
            'full_name': course.get('teacher_name')
        } if course['teacher_id'] else None
        
        course['category'] = {
            'id': course['category_id'],
            'name': course.get('category_name'),
            'description': course.get('category_description'),
            'created_at': course.get('category_created_at'),
            'updated_at': course.get('category_updated_at')
        } if course['category_id'] else None
        
        course.pop('teacher_username', None)
        course.pop('teacher_name', None)
        course.pop('category_name', None)
        course.pop('category_description', None)
        course.pop('category_created_at', None)
        course.pop('category_updated_at', None)
        
        courses.append(course)
    
    return courses


async def create_course(cursor, conn, course_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建课程"""
    # 移除None值
    course_data = exclude_none_values(course_data)
    
    sql, params = build_insert_query('courses', course_data)
    await cursor.execute(sql, params)
    await conn.commit()
    
    # 获取新创建的课程ID
    course_id = cursor.lastrowid
    
    # 返回创建的课程
    return await get_course_by_id(cursor, course_id)


async def update_course(
    cursor,
    conn,
    course_id: int,
    course_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """更新课程"""
    # 移除None值
    update_data = exclude_none_values(course_data)
    
    if not update_data:
        return await get_course_by_id(cursor, course_id)
    
    sql, params = build_update_query('courses', update_data, {'id': course_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    # 返回更新后的课程
    return await get_course_by_id(cursor, course_id)


async def delete_course(cursor, conn, course_id: int) -> bool:
    """删除课程"""
    sql, params = build_delete_query('courses', {'id': course_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    return cursor.rowcount > 0


async def get_course_count(
    cursor,
    teacher_id: Optional[int] = None,
    category_id: Optional[int] = None
) -> int:
    """获取课程总数"""
    sql = "SELECT COUNT(*) as count FROM courses"
    params = []
    where_clauses = []
    
    if teacher_id:
        where_clauses.append("teacher_id = %s")
        params.append(teacher_id)
    
    if category_id:
        where_clauses.append("category_id = %s")
        params.append(category_id)
    
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    
    await cursor.execute(sql, params)
    result = await cursor.fetchone()
    return result['count'] if result else 0
