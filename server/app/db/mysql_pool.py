"""
MySQL连接池管理
使用aiomysql进行异步MySQL操作
"""
import aiomysql
from typing import Optional
from contextlib import asynccontextmanager
from app.core.config import settings


class MySQLPool:
    """MySQL连接池管理器"""
    
    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
    
    async def create_pool(self):
        """创建连接池"""
        # 解析DATABASE_URL
        # 格式: mysql+aiomysql://user:password@host:port/database
        url = settings.DATABASE_URL.replace("mysql+aiomysql://", "")
        
        # 提取连接信息
        if "@" in url:
            credentials, host_db = url.split("@")
            if ":" in credentials:
                user, password = credentials.split(":")
            else:
                user = credentials
                password = ""
        else:
            raise ValueError("Invalid DATABASE_URL format")
        
        if "/" in host_db:
            host_port, database = host_db.split("/")
            if ":" in host_port:
                host, port = host_port.split(":")
                port = int(port)
            else:
                host = host_port
                port = 3306
        else:
            raise ValueError("Database name not specified in DATABASE_URL")
        
        self.pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=database,
            charset='utf8mb4',
            autocommit=False,
            minsize=5,
            maxsize=20,
            echo=settings.DEBUG if hasattr(settings, 'DEBUG') else False,
            pool_recycle=3600,  # 1小时回收连接
        )
        print(f"MySQL连接池已创建: {host}:{port}/{database}")
    
    async def close_pool(self):
        """关闭连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            print("MySQL连接池已关闭")
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接的上下文管理器"""
        async with self.pool.acquire() as conn:
            yield conn
    
    @asynccontextmanager
    async def get_cursor(self, dictionary=True):
        """
        获取游标的上下文管理器
        Args:
            dictionary: 如果为True，返回字典格式的结果；否则返回元组
        """
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor if dictionary else None) as cursor:
                yield cursor, conn


# 全局连接池实例
mysql_pool = MySQLPool()


async def get_db_cursor(dictionary=True):
    """
    FastAPI依赖注入函数，用于获取数据库游标
    
    Usage:
        @router.get("/")
        async def get_data(cursor_conn = Depends(get_db_cursor)):
            cursor, conn = cursor_conn
            await cursor.execute("SELECT * FROM users")
            result = await cursor.fetchall()
            return result
    """
    async with mysql_pool.get_cursor(dictionary=dictionary) as (cursor, conn):
        try:
            yield cursor, conn
        except Exception as e:
            await conn.rollback()
            raise e
        else:
            await conn.commit()


async def get_db_connection():
    """
    FastAPI依赖注入函数，用于获取数据库连接
    
    Usage:
        @router.get("/")
        async def get_data(conn = Depends(get_db_connection)):
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM users")
                result = await cursor.fetchall()
            return result
    """
    async with mysql_pool.get_connection() as conn:
        try:
            yield conn
        except Exception as e:
            await conn.rollback()
            raise e
        else:
            await conn.commit()
