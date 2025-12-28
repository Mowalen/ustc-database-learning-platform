"""
成绩查询CRUD操作 - 使用原生MySQL
"""
import csv
import io
from typing import List, Dict, Any, Iterable
from fastapi import HTTPException, status


async def get_scores_for_student(cursor, student_id: int) -> List[Dict[str, Any]]:
    """获取学生的所有成绩"""
    sql = """
        SELECT 
            s.id as submission_id,
            s.task_id,
            s.student_id,
            s.score,
            s.feedback,
            s.status,
            s.graded_at,
            t.id as task_id,
            t.course_id,
            t.title as task_title
        FROM submissions s
        JOIN tasks t ON s.task_id = t.id
        WHERE s.student_id = %s
        ORDER BY s.graded_at DESC
    """
    await cursor.execute(sql, [student_id])
    results = await cursor.fetchall()
    
    if not results:
        return []
    
    scores = []
    for row in results:
        scores.append({
            "submission_id": row['submission_id'],
            "course_id": row['course_id'],
            "task_id": row['task_id'],
            "task_title": row['task_title'],
            "student_id": row['student_id'],
            "score": row['score'],
            "feedback": row['feedback'],
            "status": row['status'],
            "graded_at": row['graded_at'],
        })
    
    return scores


async def get_scores_for_course(cursor, course_id: int) -> List[Dict[str, Any]]:
    """获取课程的所有成绩"""
    sql = """
        SELECT 
            s.id as submission_id,
            s.task_id,
            s.student_id,
            s.score,
            s.feedback,
            s.status,
            s.graded_at,
            t.id as task_id,
            t.course_id,
            t.title as task_title,
            u.username as student_username,
            u.full_name as student_name
        FROM submissions s
        JOIN tasks t ON s.task_id = t.id
        LEFT JOIN users u ON s.student_id = u.id
        WHERE t.course_id = %s
        ORDER BY s.graded_at DESC
    """
    await cursor.execute(sql, [course_id])
    results = await cursor.fetchall()
    
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No scores for course")
    
    scores = []
    for row in results:
        scores.append({
            "submission_id": row['submission_id'],
            "course_id": row['course_id'],
            "task_id": row['task_id'],
            "task_title": row['task_title'],
            "student_id": row['student_id'],
            "student_username": row.get('student_username'),
            "student_name": row.get('student_name'),
            "score": row['score'],
            "feedback": row['feedback'],
            "status": row['status'],
            "graded_at": row['graded_at'],
        })
    
    return scores


async def export_scores_csv(cursor, course_id: int) -> str:
    """导出课程成绩为CSV格式"""
    scores = await get_scores_for_course(cursor, course_id)
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["submission_id", "course_id", "task_id", "task_title", "student_id", 
                   "student_username", "student_name", "score", "status", "graded_at"],
    )
    writer.writeheader()
    writer.writerows(_coerce_to_strings(scores))
    return output.getvalue()


def _coerce_to_strings(rows: Iterable[dict]) -> Iterable[dict]:
    """将日期时间对象转换为字符串"""
    for row in rows:
        yield {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
