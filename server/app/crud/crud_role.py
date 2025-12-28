"""
角色CRUD操作 - 使用原生MySQL
"""
from typing import Optional, List, Dict, Any
from app.db.query_helper import (
    build_select_query,
    fetch_one,
    fetch_all,
)


async def get_role_by_id(cursor, role_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取角色"""
    sql = "SELECT id, name, description FROM roles WHERE id = %s"
    await cursor.execute(sql, [role_id])
    return await cursor.fetchone()


async def get_role_by_name(cursor, name: str) -> Optional[Dict[str, Any]]:
    """根据名称获取角色"""
    sql = "SELECT id, name, description FROM roles WHERE name = %s"
    await cursor.execute(sql, [name])
    return await cursor.fetchone()


async def get_all_roles(cursor) -> List[Dict[str, Any]]:
    """获取所有角色"""
    sql = "SELECT id, name, description FROM roles ORDER BY id"
    await cursor.execute(sql)
    return await cursor.fetchall()


async def create_default_roles(cursor, conn):
    """创建默认角色（如果不存在）"""
    # 检查是否已有角色
    sql = "SELECT COUNT(*) as count FROM roles"
    await cursor.execute(sql)
    result = await cursor.fetchone()
    
    if result['count'] == 0:
        # 插入默认角色
        sql = """
            INSERT INTO roles (id, name, description) VALUES
            (1, 'student', 'Student role'),
            (2, 'teacher', 'Teacher role'),
            (3, 'admin', 'Admin role')
        """
        await cursor.execute(sql)
        await conn.commit()
        return True
    return False
