# 后端迁移至 MySQL 原生连接

## 概述

本项目已从 **SQLAlchemy ORM** 迁移到使用 **aiomysql** 的原生 MySQL 连接。这大幅简化了数据库抽象层，提高了性能和可控性。

## 迁移状态

### ✅ 已完成
- [x] MySQL 连接池管理器
- [x] SQL 查询助手工具
- [x] 用户 CRUD
- [x] 角色 CRUD
- [x] 课程 CRUD
- [x] 课程章节 CRUD
- [x] 选课 CRUD
- [x] 任务和提交 CRUD
- [x] 公告 CRUD
- [x] 主应用 (main.py)
- [x] 认证路由 (auth.py)
- [x] 认证依赖 (__init__.py)

### ⚠️ 待更新
以下 router 文件仍需手动更新以使用新的数据库连接方式：
- [ ] `app/routers/users.py`
- [ ] `app/routers/courses.py`
- [ ] `app/routers/sections.py`
- [ ] `app/routers/enrollments.py`
- [ ] `app/routers/tasks.py`
- [ ] `app/routers/scores.py`
- [ ] `app/routers/admin.py`
- [ ] `app/routers/upload.py`

### 🗑️ 可删除的文件
以下文件在新架构中不再需要：
- `app/models/` 整个目录
- `app/db/session.py`
- `app/db/base.py`
- `app/crud/base.py`

## 快速开始

### 1. 配置数据库

复制并编辑环境配置文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置正确的 MySQL 连接字符串：
```env
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/ustc_learning_platform
```

### 2. 创建数据库

使用提供的 SQL schema 创建数据库：
```bash
# 方法1: 通过 MySQL 命令行
mysql -u root -p

CREATE DATABASE ustc_learning_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ustc_learning_platform;
SOURCE database_schema.sql;

# 方法2: 直接导入
mysql -u root -p ustc_learning_platform < database_schema.sql
```

### 3. 安装依赖

确保安装了必要的 Python 包：
```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install aiomysql pymysql fastapi uvicorn
```

### 4. 运行应用

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python 直接运行
python -m app.main
```

## 架构变更说明

### 数据库连接

**之前 (SQLAlchemy):**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

@router.get("/")
async def endpoint(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
```

**现在 (原生 MySQL):**
```python
from app.db.mysql_pool import get_db_cursor
from app.crud import crud_user

@router.get("/")
async def endpoint(cursor_conn = Depends(get_db_cursor)):
    cursor, conn = cursor_conn
    users = await crud_user.get_users(cursor)
```

### 数据返回格式

**之前:** ORM 对象 (可以使用 `.` 访问属性)
```python
user.id
user.username
user.role.name
```

**现在:** 字典 (使用 `[]` 或 `.get()` 访问)
```python
user['id']
user['username']
user.get('role', {}).get('name')
```

### 关系处理

**之前:** ORM 自动处理关系
```python
from sqlalchemy.orm import relationship

class User(Base):
    role = relationship("Role", back_populates="users")
```

**现在:** 手动 JOIN 查询
```python
sql = """
    SELECT u.*, r.name as role_name
    FROM users u
    LEFT JOIN roles r ON u.role_id = r.id
"""
```

## 更新 Router 指南

对于每个需要更新的 router 文件，按以下步骤操作：

### 1. 更新导入
```python
# 删除
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

# 添加
from app.db.mysql_pool import get_db_cursor
from app.crud import crud_xxx  # 相应的 CRUD 模块
```

### 2. 更新端点函数签名
```python
# 之前
async def endpoint(db: AsyncSession = Depends(get_db)):

# 现在
async def endpoint(cursor_conn = Depends(get_db_cursor)):
    cursor, conn = cursor_conn
```

### 3. 更新 CRUD 调用
```python
# 之前
user = await crud_user.get(db, id=user_id)

# 现在
user = await crud_user.get_user_by_id(cursor, user_id)
```

### 4. 更新属性访问
```python
# 之前
user.id
user.role.name

# 现在
user['id']
user.get('role', {}).get('name')
```

## 常见问题

### Q: 如何处理事务？
A: 使用 `get_db_cursor()` 依赖时，事务会自动管理：
- 函数执行成功 → 自动 `commit`
- 抛出异常 → 自动 `rollback`

如需手动控制事务：
```python
async with mysql_pool.get_cursor() as (cursor, conn):
    try:
        await cursor.execute("INSERT ...")
        await cursor.execute("UPDATE ...")
        await conn.commit()
    except Exception as e:
        await conn.rollback()
        raise
```

### Q: Pydantic schemas 还能用吗？
A: 可以！schemas 仍然用于请求验证和响应序列化。只需确保从数据库返回的字典格式与 schema 定义匹配。

### Q: 如何调试 SQL 查询？
A: 在创建连接池时已启用 `echo=True`，所有 SQL 查询会打印到控制台。

### Q: 性能如何？
A: 原生 MySQL 查询通常比 ORM 更快，特别是对于复杂查询和大批量操作。连接池也提供了更好的连接管理。

## 测试

运行测试确保迁移成功：
```bash
pytest server/tests/ -v
```

## 回滚到 SQLAlchemy

如果需要回滚，可以从 Git 历史中恢复：
```bash
git log --oneline  # 找到迁移前的提交
git revert <commit-hash>
```

## 技术栈

- **数据库**: MySQL 8.0+
- **Python**: 3.13+
- **异步驱动**: aiomysql
- **Web框架**: FastAPI
- **连接池**: aiomysql.Pool

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

请查看项目根目录的 LICENSE 文件。
