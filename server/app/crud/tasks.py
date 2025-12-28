"""
作业/考试和提交CRUD操作 - 使用原生MySQL
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
    sql = "SELECT id, teacher_id, is_active FROM courses WHERE id = %s"
    await cursor.execute(sql, [course_id])
    course = await cursor.fetchone()
    if not course or not course.get('is_active', True):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found or inactive")
    return course


async def _get_student_enrollment(cursor, course_id: int, student_id: int) -> Dict[str, Any]:
    """检查学生是否选了该课程"""
    sql = """
        SELECT id FROM course_enrollments 
        WHERE course_id = %s AND student_id = %s AND status = 'active'
    """
    await cursor.execute(sql, [course_id, student_id])
    enrollment = await cursor.fetchone()
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enrolled in course")
    return enrollment


async def create_task(cursor, conn, course_id: int, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建作业/考试"""
    course = await _get_course(cursor, course_id)
    
    # 验证教师是否匹配
    if course['teacher_id'] != task_data.get('teacher_id'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Teacher mismatch for course")
    
    task_insert_data = {
        'course_id': course_id,
        'teacher_id': task_data['teacher_id'],
        'title': task_data['title'],
        'description': task_data.get('description'),
        'type': task_data['type'],  # 'assignment' or 'exam'
        'deadline': task_data.get('deadline')
    }
    
    task_insert_data = exclude_none_values(task_insert_data)
    sql, params = build_insert_query('tasks', task_insert_data)
    await cursor.execute(sql, params)
    await conn.commit()
    
    task_id = cursor.lastrowid
    return await get_task_by_id(cursor, task_id)


async def get_task_by_id(cursor, task_id: int) -> Dict[str, Any]:
    """根据ID获取任务"""
    sql = """
        SELECT 
            t.id, t.course_id, t.teacher_id, t.title, t.description,
            t.type, t.deadline, t.created_at, t.updated_at,
            c.title as course_title
        FROM tasks t
        LEFT JOIN courses c ON t.course_id = c.id
        WHERE t.id = %s
    """
    await cursor.execute(sql, [task_id])
    result = await cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    task = dict(result)
    task['course'] = {
        'id': task['course_id'],
        'title': task.get('course_title')
    }
    task.pop('course_title', None)
    
    return task


async def list_tasks(cursor, course_id: int) -> List[Dict[str, Any]]:
    """获取课程的任务列表"""
    await _get_course(cursor, course_id)
    
    sql = """
        SELECT 
            id, course_id, teacher_id, title, description,
            type, deadline, created_at, updated_at
        FROM tasks
        WHERE course_id = %s
        ORDER BY created_at DESC
    """
    await cursor.execute(sql, [course_id])
    return await cursor.fetchall()


async def submit_task(cursor, conn, task_id: int, submission_data: Dict[str, Any]) -> Dict[str, Any]:
    """提交作业/考试"""
    task = await get_task_by_id(cursor, task_id)
    await _get_student_enrollment(cursor, task['course_id'], submission_data['student_id'])
    
    # 检查是否逾期
    now = datetime.now()
    status_value = 'submitted'
    
    if task.get('deadline') and now > task['deadline']:
        status_value = 'late'
    
    # 检查是否已经提交过
    sql = "SELECT id FROM submissions WHERE task_id = %s AND student_id = %s"
    await cursor.execute(sql, [task_id, submission_data['student_id']])
    existing = await cursor.fetchone()
    
    if existing:
        # 更新已有提交
        update_data = {
            'answer_text': submission_data.get('answer_text'),
            'file_url': submission_data.get('file_url'),
            'status': status_value,
            'submitted_at': now
        }
        update_data = exclude_none_values(update_data)
        sql, params = build_update_query('submissions', update_data, {'id': existing['id']})
        await cursor.execute(sql, params)
        await conn.commit()
        submission_id = existing['id']
    else:
        # 创建新提交
        submission_insert = {
            'task_id': task_id,
            'student_id': submission_data['student_id'],
            'answer_text': submission_data.get('answer_text'),
            'file_url': submission_data.get('file_url'),
            'status': status_value,
            'submitted_at': now
        }
        submission_insert = exclude_none_values(submission_insert)
        sql, params = build_insert_query('submissions', submission_insert)
        await cursor.execute(sql, params)
        await conn.commit()
        submission_id = cursor.lastrowid
    
    return await get_submission_by_id(cursor, submission_id)


async def get_submission_by_id(cursor, submission_id: int) -> Dict[str, Any]:
    """根据ID获取提交记录"""
    sql = """
        SELECT 
            s.id, s.task_id, s.student_id, s.answer_text, s.file_url,
            s.score, s.feedback, s.submitted_at, s.graded_at, s.status,
            t.title as task_title, t.course_id,
            u.username as student_username, u.full_name as student_name
        FROM submissions s
        LEFT JOIN tasks t ON s.task_id = t.id
        LEFT JOIN users u ON s.student_id = u.id
        WHERE s.id = %s
    """
    await cursor.execute(sql, [submission_id])
    result = await cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    
    submission = dict(result)
    submission['task'] = {
        'id': submission['task_id'],
        'title': submission.get('task_title'),
        'course_id': submission.get('course_id')
    }
    submission['student'] = {
        'id': submission['student_id'],
        'username': submission.get('student_username'),
        'full_name': submission.get('student_name')
    }
    submission.pop('task_title', None)
    submission.pop('course_id', None)
    submission.pop('student_username', None)
    submission.pop('student_name', None)
    
    return submission


async def apply_grade(cursor, conn, submission_id: int, grade_data: Dict[str, Any]) -> Dict[str, Any]:
    """批改作业/考试"""
    update_data = {
        'score': grade_data.get('score'),
        'feedback': grade_data.get('feedback'),
        'status': grade_data.get('status', 'graded'),
        'graded_at': datetime.now()
    }
    
    update_data = exclude_none_values(update_data)
    sql, params = build_update_query('submissions', update_data, {'id': submission_id})
    await cursor.execute(sql, params)
    await conn.commit()
    
    return await get_submission_by_id(cursor, submission_id)


async def list_submissions(cursor, task_id: int) -> List[Dict[str, Any]]:
    """获取任务的所有提交"""
    sql = """
        SELECT 
            s.id, s.task_id, s.student_id, s.answer_text, s.file_url,
            s.score, s.feedback, s.submitted_at, s.graded_at, s.status,
            u.username as student_username, u.full_name as student_name,
            u.role_id, r.name as role_name
        FROM submissions s
        LEFT JOIN users u ON s.student_id = u.id
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE s.task_id = %s
        ORDER BY s.submitted_at DESC
    """
    await cursor.execute(sql, [task_id])
    results = await cursor.fetchall()
    
    submissions = []
    for result in results:
        submission = dict(result)
        submission['student'] = {
            'id': submission['student_id'],
            'username': submission.get('student_username'),
            'full_name': submission.get('student_name'),
            'role_id': submission.get('role_id'),
            'role': {
                'id': submission.get('role_id'),
                'name': submission.get('role_name')
            }
        }
        submission.pop('student_username', None)
        submission.pop('student_name', None)
        submission.pop('role_id', None)
        submission.pop('role_name', None)
        submissions.append(submission)
    
    return submissions


async def get_student_submissions(cursor, student_id: int, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """获取学生的所有提交"""
    sql = """
        SELECT 
            s.id, s.task_id, s.student_id, s.answer_text, s.file_url,
            s.score, s.feedback, s.submitted_at, s.graded_at, s.status,
            t.title as task_title, t.type as task_type, t.deadline,
            t.course_id
        FROM submissions s
        LEFT JOIN tasks t ON s.task_id = t.id
        WHERE s.student_id = %s
    """
    params = [student_id]
    
    if course_id:
        sql += " AND t.course_id = %s"
        params.append(course_id)
    
    sql += " ORDER BY s.submitted_at DESC"
    
    await cursor.execute(sql, params)
    results = await cursor.fetchall()
    
    submissions = []
    for result in results:
        submission = dict(result)
        submission['task'] = {
            'id': submission['task_id'],
            'title': submission.get('task_title'),
            'type': submission.get('task_type'),
            'deadline': submission.get('deadline'),
            'course_id': submission.get('course_id')
        }
        submission.pop('task_title', None)
        submission.pop('task_type', None)
        submission.pop('deadline', None)
        submission.pop('course_id', None)
        submissions.append(submission)
    
    return submissions
