"""
SQL查询助手函数
提供构建和执行SQL查询的工具函数
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


def build_insert_query(table: str, data: Dict[str, Any]) -> Tuple[str, List]:
    """
    构建INSERT查询
    
    Args:
        table: 表名
        data: 要插入的数据字典
    
    Returns:
        (SQL查询字符串, 参数列表)
    
    Example:
        sql, params = build_insert_query("users", {"username": "john", "email": "john@example.com"})
        # 返回: ("INSERT INTO users (username, email) VALUES (%s, %s)", ["john", "john@example.com"])
    """
    columns = list(data.keys())
    placeholders = ["%s"] * len(columns)
    values = [data[col] for col in columns]
    
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
    return sql, values


def build_update_query(table: str, data: Dict[str, Any], where: Dict[str, Any]) -> Tuple[str, List]:
    """
    构建UPDATE查询
    
    Args:
        table: 表名
        data: 要更新的数据字典
        where: WHERE条件字典
    
    Returns:
        (SQL查询字符串, 参数列表)
    
    Example:
        sql, params = build_update_query("users", {"email": "new@example.com"}, {"id": 1})
        # 返回: ("UPDATE users SET email = %s WHERE id = %s", ["new@example.com", 1])
    """
    set_parts = [f"{col} = %s" for col in data.keys()]
    where_parts = [f"{col} = %s" for col in where.keys()]
    
    values = list(data.values()) + list(where.values())
    
    sql = f"UPDATE {table} SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"
    return sql, values


def build_select_query(
    table: str,
    columns: List[str] = None,
    where: Dict[str, Any] = None,
    order_by: str = None,
    limit: int = None,
    offset: int = None,
    joins: List[Dict[str, str]] = None
) -> Tuple[str, List]:
    """
    构建SELECT查询
    
    Args:
        table: 主表名
        columns: 要选择的列列表，None表示选择所有列
        where: WHERE条件字典
        order_by: 排序字段，如 "created_at DESC"
        limit: 限制返回行数
        offset: 偏移量
        joins: JOIN子句列表，如 [{"type": "LEFT JOIN", "table": "roles", "on": "users.role_id = roles.id"}]
    
    Returns:
        (SQL查询字符串, 参数列表)
    """
    # SELECT部分
    if columns:
        select_cols = ', '.join(columns)
    else:
        select_cols = '*'
    
    sql = f"SELECT {select_cols} FROM {table}"
    params = []
    
    # JOIN部分
    if joins:
        for join in joins:
            sql += f" {join['type']} {join['table']} ON {join['on']}"
    
    # WHERE部分
    if where:
        where_parts = [f"{col} = %s" for col in where.keys()]
        sql += f" WHERE {' AND '.join(where_parts)}"
        params.extend(where.values())
    
    # ORDER BY部分
    if order_by:
        sql += f" ORDER BY {order_by}"
    
    # LIMIT部分
    if limit:
        sql += f" LIMIT {limit}"
        if offset:
            sql += f" OFFSET {offset}"
    
    return sql, params


def build_delete_query(table: str, where: Dict[str, Any]) -> Tuple[str, List]:
    """
    构建DELETE查询
    
    Args:
        table: 表名
        where: WHERE条件字典
    
    Returns:
        (SQL查询字符串, 参数列表)
    """
    where_parts = [f"{col} = %s" for col in where.keys()]
    values = list(where.values())
    
    sql = f"DELETE FROM {table} WHERE {' AND '.join(where_parts)}"
    return sql, values


async def execute_query(cursor, sql: str, params: List = None) -> int:
    """
    执行SQL查询（INSERT, UPDATE, DELETE）
    
    Args:
        cursor: 数据库游标
        sql: SQL查询字符串
        params: 查询参数列表
    
    Returns:
        受影响的行数
    """
    await cursor.execute(sql, params or [])
    return cursor.rowcount


async def fetch_one(cursor, sql: str, params: List = None) -> Optional[Dict[str, Any]]:
    """
    执行SELECT查询并返回一行结果
    
    Args:
        cursor: 数据库游标（必须是DictCursor）
        sql: SQL查询字符串
        params: 查询参数列表
    
    Returns:
        结果字典或None
    """
    await cursor.execute(sql, params or [])
    return await cursor.fetchone()


async def fetch_all(cursor, sql: str, params: List = None) -> List[Dict[str, Any]]:
    """
    执行SELECT查询并返回所有结果
    
    Args:
        cursor: 数据库游标（必须是DictCursor）
        sql: SQL查询字符串
        params: 查询参数列表
    
    Returns:
        结果字典列表
    """
    await cursor.execute(sql, params or [])
    return await cursor.fetchall()


def convert_datetime_to_str(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    将字典中的datetime对象转换为字符串
    
    Args:
        data: 数据字典
    
    Returns:
        转换后的字典
    """
    if not data:
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


def exclude_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    从字典中排除值为None的键
    
    Args:
        data: 数据字典
    
    Returns:
        过滤后的字典
    """
    return {k: v for k, v in data.items() if v is not None}
