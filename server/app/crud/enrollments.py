"""
选课CRUD操作 - 使用原生MySQL
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from app.db.query_helper import (
    build_insert_query,
    build_update_query,
    exclude_none_values
)


async def _get_course(cursor, course_id: int) -> Dict[str, Any]:
    """获取课程（辅助函数）"""
    sql = "SELECT id, is_active FROM courses WHERE id = %s"
    await cursor.execute(sql, [course_id])
    course = await cursor.fetchone()
    if not course or not course.get('is_active', True):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or inactive")
    return course


async def _get_student(cursor, student_id: int) -> Dict[str, Any]:
    """获取学生（辅助函数）"""
    sql = "SELECT id, is_active, role_id FROM users WHERE id = %s"
    await cursor.execute(sql, [student_id])
    student = await cursor.fetchone()
    if not student or not student.get('is_active', True):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or inactive")
    return student


async def enroll_student(cursor, conn, course_id: int, student_id: int) -> Dict[str, Any]:
    """学生选课"""
    await _get_course(cursor, course_id)
    await _get_student(cursor, student_id)
    
    # 检查是否已经选课
    sql = "SELECT id, status FROM course_enrollments WHERE course_id = %s AND student_id = %s"
    await cursor.execute(sql, [course_id, student_id])
    enrollment = await cursor.fetchone()
    
    if enrollment:
        if enrollment['status'] == 'dropped':
            # 重新激活选课
            sql = "UPDATE course_enrollments SET status = 'active', enrolled_at = %s WHERE id = %s"
            await cursor.execute(sql, [datetime.now(), enrollment['id']])
            await conn.commit()
            enrollment_id = enrollment['id']
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already enrolled")
    else:
        # 创建新的选课记录
        enrollment_data = {
            'course_id': course_id,
            'student_id': student_id,
            'status': 'active',
            'enrolled_at': datetime.now()
        }
        sql, params = build_insert_query('course_enrollments', enrollment_data)
        await cursor.execute(sql, params)
        await conn.commit()
        enrollment_id = cursor.lastrowid
    
    # 返回完整的选课信息
    return await get_enrollment_by_id(cursor, enrollment_id)


async def drop_course(cursor, conn, course_id: int, student_id: int) -> Dict[str, Any]:
    """学生退课"""
    await _get_course(cursor, course_id)
    await _get_student(cursor, student_id)
    
    sql = "SELECT id, status FROM course_enrollments WHERE course_id = %s AND student_id = %s"
    await cursor.execute(sql, [course_id, student_id])
    enrollment = await cursor.fetchone()
    
    if not enrollment or enrollment['status'] == 'dropped':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    
    # 更新状态为dropped
    sql = "UPDATE course_enrollments SET status = 'dropped' WHERE id = %s"
    await cursor.execute(sql, [enrollment['id']])
    await conn.commit()
    
    return await get_enrollment_by_id(cursor, enrollment['id'])


async def get_enrollment_by_id(cursor, enrollment_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取选课记录"""
    sql = """
        SELECT 
            e.id, e.course_id, e.student_id, e.enrolled_at, e.status,
            c.title as course_title, c.teacher_id, c.is_active as course_is_active,
            u.username as student_username, u.full_name as student_name,
            u.role_id as student_role_id
        FROM course_enrollments e
        LEFT JOIN courses c ON e.course_id = c.id
        LEFT JOIN users u ON e.student_id = u.id
        WHERE e.id = %s
    """
    await cursor.execute(sql, [enrollment_id])
    result = await cursor.fetchone()
    
    if result:
        enrollment = dict(result)
        enrollment['course'] = {
            'id': enrollment['course_id'],
            'title': enrollment.get('course_title'),
            'teacher_id': enrollment.get('teacher_id'),
            'is_active': enrollment.get('course_is_active')
        }
        enrollment['student'] = {
            'id': enrollment['student_id'],
            'username': enrollment.get('student_username'),
            'full_name': enrollment.get('student_name'),
            'role_id': enrollment.get('student_role_id')
        }
        enrollment.pop('course_title', None)
        enrollment.pop('teacher_id', None)
        enrollment.pop('course_is_active', None)
        enrollment.pop('student_username', None)
        enrollment.pop('student_name', None)
        enrollment.pop('student_role_id', None)
    
    return result


async def list_student_enrollments(cursor, student_id: int) -> List[Dict[str, Any]]:
    """获取学生的选课列表"""
    await _get_student(cursor, student_id)
    
    sql = """
        SELECT 
            e.id, e.course_id, e.student_id, e.enrolled_at, e.status,
            c.title as course_title, c.description as course_description,
            c.teacher_id, c.cover_url, c.is_active as course_is_active
        FROM course_enrollments e
        LEFT JOIN courses c ON e.course_id = c.id
        WHERE e.student_id = %s AND e.status = 'active'
        ORDER BY e.enrolled_at DESC
    """
    await cursor.execute(sql, [student_id])
    results = await cursor.fetchall()
    
    enrollments = []
    for result in results:
        enrollment = dict(result)
        enrollment['course'] = {
            'id': enrollment['course_id'],
            'title': enrollment.get('course_title'),
            'description': enrollment.get('course_description'),
            'teacher_id': enrollment.get('teacher_id'),
            'cover_url': enrollment.get('cover_url'),
            'is_active': enrollment.get('course_is_active')
        }
        enrollment.pop('course_title', None)
        enrollment.pop('course_description', None)
        enrollment.pop('course_is_active', None)
        enrollment.pop('teacher_id', None)
        enrollment.pop('cover_url', None)
        enrollments.append(enrollment)
    
    return enrollments


async def list_course_students(cursor, course_id: int) -> List[Dict[str, Any]]:
    """获取课程的学生列表"""
    await _get_course(cursor, course_id)
    
    sql = """
        SELECT 
            e.id, e.course_id, e.student_id, e.enrolled_at, e.status,
            u.username as student_username, u.full_name as student_name,
            u.email as student_email, u.role_id as student_role_id,
            r.name as role_name
        FROM course_enrollments e
        LEFT JOIN users u ON e.student_id = u.id
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE e.course_id = %s AND e.status = 'active'
        ORDER BY e.enrolled_at DESC
    """
    await cursor.execute(sql, [course_id])
    results = await cursor.fetchall()
    
    enrollments = []
    for result in results:
        enrollment = dict(result)
        enrollment['student'] = {
            'id': enrollment['student_id'],
            'username': enrollment.get('student_username'),
            'full_name': enrollment.get('student_name'),
            'email': enrollment.get('student_email'),
            'role_id': enrollment.get('student_role_id'),
            'role': {
                'id': enrollment.get('student_role_id'),
                'name': enrollment.get('role_name')
            }
        }
        enrollment.pop('student_username', None)
        enrollment.pop('student_name', None)
        enrollment.pop('student_email', None)
        enrollment.pop('student_role_id', None)
        enrollment.pop('role_name', None)
        enrollments.append(enrollment)
    
    return enrollments


async def get_enrollment_count(cursor, course_id: Optional[int] = None, student_id: Optional[int] = None) -> int:
    """获取选课总数"""
    sql = "SELECT COUNT(*) as count FROM course_enrollments WHERE status = 'active'"
    params = []
    
    if course_id:
        sql += " AND course_id = %s"
        params.append(course_id)
    
    if student_id:
        sql += " AND student_id = %s"
        params.append(student_id)
    
    await cursor.execute(sql, params)
    result = await cursor.fetchone()
    return result['count'] if result else 0
