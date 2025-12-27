# 测试指南

## 📋 测试概览

本测试套件覆盖了所有39个后端API接口，包括：
- ✅ 认证接口 (2个)
- ✅ 用户接口 (2个)
- ✅ 课程接口 (7个)
- ✅ 章节接口 (5个)
- ✅ 选课接口 (4个)
- ✅ 任务与提交接口 (5个)
- ✅ 成绩接口 (3个)
- ✅ 管理员接口 (8个)
- ✅ 文件上传接口 (3个)

## 🚀 快速开始

### 前置条件

1. 确保后端服务正在运行：
```powershell
cd server
python main.py
```

服务应该运行在 `http://localhost:8000`

2. 安装测试依赖：
```powershell
pip install pytest pytest-asyncio httpx
```

### 运行所有测试

```powershell
# 在 server 目录下运行
cd server
pytest tests/ -v
```

### 运行特定测试文件

```powershell
# 测试认证接口
pytest tests/test_auth.py -v

# 测试用户接口
pytest tests/test_users.py -v

# 测试课程接口
pytest tests/test_courses.py -v

# 测试章节接口
pytest tests/test_sections.py -v

# 测试选课接口
pytest tests/test_enrollments.py -v

# 测试任务接口
pytest tests/test_tasks.py -v

# 测试成绩接口
pytest tests/test_scores.py -v

# 测试管理员接口
pytest tests/test_admin.py -v

# 测试文件上传接口
pytest tests/test_upload.py -v

# 测试所有接口（综合测试）
pytest tests/test_all_endpoints.py -v
```

### 运行特定测试用例

```powershell
# 运行特定测试类
pytest tests/test_auth.py::TestAuth -v

# 运行特定测试方法
pytest tests/test_auth.py::TestAuth::test_login_success -v

# 运行包含特定关键字的测试
pytest tests/ -k "upload" -v
```

## 📊 测试文件说明

### 核心测试文件

| 文件 | 说明 | 覆盖接口数 |
|------|------|-----------|
| `test_auth.py` | 认证相关测试（注册、登录） | 2 |
| `test_users.py` | 用户管理测试（当前用户信息、更新） | 2 |
| `test_courses.py` | 课程管理测试（CRUD、分类） | 7 |
| `test_sections.py` | 章节管理测试（CRUD） | 5 |
| `test_enrollments.py` | 选课管理测试（选课、退课、查询） | 4 |
| `test_tasks.py` | 任务管理测试（创建、提交、评分） | 5 |
| `test_scores.py` | 成绩管理测试（查询、导出） | 3 |
| `test_admin.py` | 管理员功能测试（用户、课程、公告管理） | 8 |
| `test_upload.py` | 文件上传测试（文件、图片、头像） | 3 |
| `test_all_endpoints.py` | **综合测试（覆盖所有39个接口）** | 39 |

### 辅助文件

- `conftest.py` - Pytest配置和公共fixture
- `test_integration.py` - 集成测试
- `test_api_flow.py` - API流程测试

## 🎯 测试覆盖率

### 按模块统计

```
认证模块:    100% (2/2)
用户模块:    100% (2/2)
课程模块:    100% (7/7)
章节模块:    100% (5/5)
选课模块:    100% (4/4)
任务模块:    100% (5/5)
成绩模块:    100% (3/3)
管理员模块:  100% (8/8)
文件上传模块: 100% (3/3)
━━━━━━━━━━━━━━━━━━━━━━━━━
总计:        100% (39/39)
```

## 🔧 高级用法

### 生成测试报告

```powershell
# 生成HTML报告
pytest tests/ --html=report.html --self-contained-html

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

### 并行运行测试

```powershell
# 安装 pytest-xdist
pip install pytest-xdist

# 使用4个进程并行运行
pytest tests/ -n 4
```

### 调试模式

```powershell
# 显示print输出
pytest tests/ -v -s

# 在第一个失败时停止
pytest tests/ -x

# 显示最详细的输出
pytest tests/ -vv
```

## 📝 编写新测试

### 示例：测试新接口

```python
# tests/test_my_feature.py
import pytest
from httpx import AsyncClient
from typing import Dict

@pytest.mark.asyncio
async def test_my_new_endpoint(client: AsyncClient, teacher_headers: Dict[str, str]):
    """测试我的新接口"""
    response = await client.get("/my-endpoint", headers=teacher_headers)
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

### 可用的Fixtures

- `client` - 异步HTTP客户端
- `teacher_token` / `teacher_headers` - 教师认证
- `student_token` / `student_headers` - 学生认证
- `admin_token` / `admin_headers` - 管理员认证
- `test_course` - 测试课程
- `test_section` - 测试章节
- `course_category` - 课程分类

## ⚠️ 注意事项

1. **数据库状态**: 测试使用实际数据库，可能会创建测试数据。建议使用独立的测试数据库。

2. **服务运行**: 确保后端服务在运行测试前已启动。

3. **端口冲突**: 默认使用8000端口，如果修改了端口，需要在`conftest.py`中更新。

4. **并发测试**: 部分测试可能不适合并行运行（如创建同名资源）。

5. **清理数据**: 测试会创建数据但不会自动清理，建议定期重置测试数据库。

## 🐛 常见问题

### 测试失败：Connection refused

**原因**: 后端服务未运行

**解决**: 先启动后端服务 `python main.py`

### 测试失败：401 Unauthorized

**原因**: 认证token失效或配置错误

**解决**: 检查conftest.py中的认证配置

### 测试失败：已存在的用户名

**原因**: 之前的测试创建了相同用户名

**解决**: 测试使用UUID生成唯一用户名，或重置数据库

## 📈 持续集成

### GitHub Actions 示例

```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx
      - name: Run tests
        run: pytest tests/ -v
```

## 📞 支持

如果遇到问题，请：
1. 查看测试输出的详细错误信息
2. 检查后端服务日志
3. 确认数据库连接正常
4. 查阅API文档：`../API.md`

---

**最后更新**: 2025-12-27
**测试框架**: pytest + pytest-asyncio + httpx
**Python版本**: 3.13+
