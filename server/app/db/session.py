from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 根据数据库类型设置不同的连接参数
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}
elif "mysql" in settings.DATABASE_URL:
    # MySQL 连接池配置
    connect_args = {
        "charset": "utf8mb4",
    }

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # 生产环境建议设为 False
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True,  # 连接池健康检查
    pool_recycle=3600,   # 1小时回收连接，防止 MySQL 超时
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
