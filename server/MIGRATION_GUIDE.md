# SQLAlchemy 到 MySQL 原生连接迁移指南

## 概述
本项目已从 SQLAlchemy ORM 迁移到使用 aiomysql 的原生 MySQL 连接。

## 已完成的迁移

### 1. 核心基础设施
- ✅ **MySQL 连接池** (`app/db/mysql_pool.py`)
  - 创建了连接池管理器
  - 提供 `get_db_cursor()` 和 `get_db_connection()` 依赖注入函数

- ✅ **查询助手** (`app/db/query_helper.py`)
  - 提供构建 SQL 查询的工具函数
  - `build_insert_query()`, `build_update_query()`, `build_select_query()`, `build_delete_query()`
  - 执行查询的助手函数：`fetch_one()`, `fetch_all()`, `execute_query()`

### 2. CRUD 操作
- ✅ **用户 CRUD** (`app/crud/crud_user.py`)
- ✅ **角色 CRUD** (`app/crud/crud_role.py`)
- ✅ **课程 CRUD** (`app/crud/crud_course.py`)

### 3. 路由
- ✅ **主应用** (`app/main.py`) - 使用连接池替代 SQLAlchemy
- ✅ **认证路由** (`app/routers/auth.py`)
- ✅ **认证依赖** (`app/routers/__init__.py`)

## 待迁移的文件

### CRUD 文件需要重构

1. **`app/crud/base.py`** - ❌ 需要删除或重构
   - 这个文件包含 SQLAlchemy 的通用 CRUD 基类
   - 建议：删除此文件，因为不再使用 ORM

2. **`app/crud/crud_section.py`** - ⚠️ 需要重构
   ```python
   # 需要迁移为原生 MySQL 查询
   async def get_section_by_id(cursor, section_id: int)
   async def get_sections_by_course(cursor, course_id: int)
   async def create_section(cursor, conn, section_data: Dict)
   async def update_section(cursor, conn, section_id: int, section_data: Dict)
   async def delete_section(cursor, conn, section_id: int)
   ```

3. **`app/crud/enrollments.py`** - ⚠️ 需要重构
4. **`app/crud/tasks.py`** - ⚠️ 需要重构
5. **`app/crud/scores.py`** - ⚠️ 需要重构
6. **`app/crud/admin.py`** - ⚠️ 需要重构

### Router 文件需要更新

所有 router 文件都需要：
1. 移除 `from sqlalchemy.ext.asyncio import AsyncSession`
2. 移除 `from app.db.session import get_db`
3. 添加 `from app.db.mysql_pool import get_db_cursor`
4. 将所有 `db: AsyncSession = Depends(get_db)` 改为 `cursor_conn = Depends(get_db_cursor)`
5. 在函数开始处添加 `cursor, conn = cursor_conn`
6. 更新 CRUD 调用以传递 `cursor` 和 `conn`

需要更新的 router 文件：
- ⚠️ `app/routers/users.py`
- ⚠️ `app/routers/courses.py`
- ⚠️ `app/routers/sections.py`
- ⚠️ `app/routers/enrollments.py`
- ⚠️ `app/routers/tasks.py`
- ⚠️ `app/routers/scores.py`
- ⚠️ `app/routers/admin.py`
- ⚠️ `app/routers/upload.py`

### Models 目录
- ❌ **整个 `app/models/` 目录可以删除**
  - 不再需要 ORM 模型
  - 数据库 schema 由 `database_schema.sql` 定义

### 数据库配置
- ❌ **`app/db/session.py`** - 可以删除
- ❌ **`app/db/base.py`** - 可以删除

## 迁移模式

### 典型的 Router 函数迁移示例

**迁移前（SQLAlchemy）：**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.crud_user import user as crud_user

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**迁移后（原生 MySQL）：**
```python
from app.db.mysql_pool import get_db_cursor
from app.crud import crud_user

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    cursor_conn = Depends(get_db_cursor)
):
    cursor, conn = cursor_conn
    user = await crud_user.get_user_by_id(cursor, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 典型的 CRUD 函数重构示例

**迁移前（SQLAlchemy）：**
```python
async def get_course(db: AsyncSession, course_id: int):
    result = await db.execute(select(Course).filter(Course.id == course_id))
    return result.scalars().first()
```

**迁移后（原生 MySQL）：**
```python
async def get_course_by_id(cursor, course_id: int) -> Optional[Dict[str, Any]]:
    sql = """
        SELECT 
            c.id, c.teacher_id, c.title, c.description,
            u.username as teacher_username
        FROM courses c
        LEFT JOIN users u ON c.teacher_id = u.id
        WHERE c.id = %s
    """
    await cursor.execute(sql, [course_id])
    result = await cursor.fetchone()
    
    if result:
        course = dict(result)
        course['teacher'] = {
            'id': course['teacher_id'],
            'username': course.get('teacher_username')
        }
        course.pop('teacher_username', None)
    
    return result
```

## 数据库连接配置

确保 `.env` 文件包含正确的 MySQL 连接字符串：

```env
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/ustc_learning_platform
```

## 依赖更新

从 `pyproject.toml` 中移除（可选）：
- `sqlalchemy`

保留（必需）：
- `aiomysql`
- `pymysql`

## 数据库初始化

使用 SQL 脚本初始化数据库：
```bash
mysql -u username -p ustc_learning_platform < database_schema.sql
```

## 注意事项

1. **事务处理**：
   - 使用 `get_db_cursor()` 依赖时，事务自动管理
   - 成功时自动 commit，异常时自动 rollback

2. **结果格式**：
   - 所有查询结果都是字典（使用 `DictCursor`）
   - ORM 对象属性访问 (`user.id`) 改为字典访问 (`user['id']`)

3. **关系处理**：
   - 不再有自动的 relationship 加载
   - 需要手动编写 JOIN 查询
   - 需要手动构建嵌套的数据结构

4. **Schema 验证**：
   - Pydantic schemas 仍然有效
   - 但需要确保从数据库返回的字典格式与 schema 匹配

## 迁移检查清单

- [x] 创建 MySQL 连接池管理器
- [x] 创建 SQL 查询助手
- [x] 重构用户 CRUD
- [x] 重构角色 CRUD
- [x] 重构课程 CRUD
- [x] 更新主应用 lifespan
- [x] 更新认证路由
- [x] 更新认证依赖
- [ ] 重构课程章节 CRUD
- [ ] 重构选课 CRUD
- [ ] 重构任务 CRUD
- [ ] 重构提交 CRUD
- [ ] 重构公告 CRUD
- [ ] 更新所有 router 文件
- [ ] 更新中间件（如果需要）
- [ ] 删除不需要的文件（models, session.py, base.py）
- [ ] 更新测试文件
- [ ] 验证所有 API 端点

## 测试

确保在迁移后测试所有 API 端点：
```bash
pytest server/tests/
```
