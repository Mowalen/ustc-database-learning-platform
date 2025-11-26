# 🧪 API 测试完整指南

## ✅ 已创建的测试文件

### 完整的测试套件：

1. **conftest.py** - Pytest 配置和共享 fixtures
2. **test_auth.py** - 认证接口测试（6个测试）
3. **test_users.py** - 用户管理测试（5个测试）
4. **test_courses.py** - 课程管理测试（11个测试）
5. **test_sections.py** - 章节管理测试（11个测试）
6. **test_integration.py** - 集成测试（3个测试）
7. **test_api_flow.py** - 原有的流程测试（1个测试）

**总共：37 个测试用例**

## 🚀 快速开始

### 步骤 1：启动后端服务器

在**第一个终端**中运行：

```bash
cd server/app
uv run main.py
```

等待看到：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 步骤 2：运行测试

在**第二个终端**中运行（保持第一个终端的服务器运行）：

```bash
cd server
uv run pytest tests/ -v
```

## 📋 运行特定测试

### 运行所有测试
```bash
uv run pytest tests/ -v
```

### 逐个模块运行

```bash
# 只测试认证功能
uv run pytest tests/test_auth.py -v

# 只测试用户管理
uv run pytest tests/test_users.py -v

# 只测试课程功能
uv run pytest tests/test_courses.py -v

# 只测试章节功能
uv run pytest tests/test_sections.py -v

# 只测试集成流程
uv run pytest tests/test_integration.py -v

# 运行原有的流程测试
uv run pytest tests/test_api_flow.py -v
```

### 运行特定测试类

```bash
uv run pytest tests/test_courses.py::TestCourses -v
uv run pytest tests/test_courses.py::TestCourseCategories -v
```

### 运行单个测试用例

```bash
uv run pytest tests/test_auth.py::TestAuth::test_login_success -v
```

## 📊 测试输出选项

### 显示详细信息
```bash
# 显示每个测试的详细输出
uv run pytest tests/ -vv

# 显示 print 语句输出
uv run pytest tests/ -v -s

# 显示失败的完整堆栈
uv run pytest tests/ -v --tb=long

# 只显示简短的失败信息
uv run pytest tests/ -v --tb=short
```

### 停在第一个失败
```bash
uv run pytest tests/ -v -x
```

### 只运行上次失败的测试
```bash
uv run pytest tests/ -v --lf
```

## 🎯 测试覆盖的API端点

### ✅ 认证 (6 tests)
- 注册新用户
- 重复用户名注册
- 登录成功
- 错误密码登录
- 不存在用户登录
- 缺少字段注册

### ✅ 用户管理 (5 tests)
- 获取当前用户信息
- 未授权访问
- 更新用户信息
- 更新密码
- 无效 token

### ✅ 课程管理 (11 tests)
- 创建课程
- 列出课程
- 获取课程详情
- 获取不存在的课程
- 更新课程
- 未授权更新
- 删除课程
- 未授权创建
- 创建分类
- 列出分类
- 分页查询

### ✅ 章节管理 (11 tests)
- 创建章节
- 错误的 course_id
- 列出课程章节
- 获取章节详情
- 获取不存在的章节
- 更新章节
- 未授权更新
- 删除章节
- 未授权创建
- 分页查询

### ✅ 集成测试 (3 tests)
- 教师完整工作流
- 学生完整工作流
- 权限检查

### ✅ API Flow (1 test)
- 完整的课程创建流程

## ⚠️ 常见问题

### 问题1：所有测试失败，提示连接错误

**错误信息**：`Connection refused` 或 `All connection attempts failed`

**原因**：后端服务器没有运行

**解决方法**：
1. 打开新终端
2. 运行 `cd server/app`
3. 运行 `uv run main.py`
4. 确保看到 "Application startup complete"
5. 然后在另一个终端运行测试

### 问题2：测试显示 "async def functions are not natively supported"

** 原因**：pytest-asyncio 未正确配置

**解决方法**：
- 确保测试函数有 `@pytest.mark.asyncio` 装饰器
- 已经修复，重新运行即可

### 问题3：部分测试失败，提示 "already exists"

**原因**：之前运行过测试，数据已存在

**解决方法**：
- 这是正常的，fixtures 会自动处理
- 或者清空数据库后重新运行

### 问题4：端口被占用

**错误信息**：`Address already in use`

**解决方法**：
1. 停止占用 8000 端口的进程
2. 或修改 `conftest.py` 中的 `BASE_URL`

## 📈 查看测试报告

### 生成HTML报告
```bash
uv pip install pytest-html
uv run pytest tests/ --html=report.html --self-contained-html
```

然后在浏览器中打开 `report.html`

### 生成覆盖率报告
```bash
uv pip install pytest-cov
uv run pytest tests/ --cov=app --cov-report=html
```

然后在浏览器中打开 `htmlcov/index.html`

## 🔧 调试测试

### 进入调试模式
```bash
uv run pytest tests/test_auth.py::TestAuth::test_login_success -vv --pdb
```

### 查看完整输出
```bash
uv run pytest tests/ -vv -s --tb=long
```

## 📝 测试统计

```bash
# 快速统计测试数量
uv run pytest tests/ --collect-only

# 查看测试执行时间
uv run pytest tests/ -v --durations=10
```

## ✨ 成功运行示例

成功运行后你应该看到类似这样的输出：

```
============================= test session starts ==============================
collected 37 items

tests/test_api_flow.py::test_flow PASSED                                  [  2%]
tests/test_auth.py::TestAuth::test_register_new_user PASSED               [  5%]
tests/test_auth.py::TestAuth::test_register_duplicate_username PASSED     [  8%]
tests/test_auth.py::TestAuth::test_login_success PASSED                   [ 10%]
...
tests/test_integration.py::TestCompleteFlow::test_unauthorized_actions PASSED [100%]

============================== 37 passed in 5.23s ===============================
```

## 🎓 下一步

1. **扩展测试**：为新功能添加测试
2. **CI/CD 集成**：在 GitHub Actions 中自动运行
3. **性能测试**：添加负载测试
4. **E2E 测试**：添加前后端集成测试

## 📚 相关文档

- [Pytest 官方文档](https://docs.pytest.org/)
- [HTTPX 文档](https://www.python-httpx.org/)
- [FastAPI 测试指南](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
