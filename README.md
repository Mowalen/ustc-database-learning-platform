# USTC 数据库学习平台 (Database Learning Platform)

本项目是中国科学技术大学（USTC）数据库课程设计的项目成果。这是一个现代化的全栈 Web 应用，旨在为数据库教学提供一个全面的管理平台。系统集成了课程管理、在线作业提交、自动/手动评分、公告发布以及多角色权限管理等功能，为教师和学生提供便捷、高效的教学辅助体验。

## 📚 项目资源
- **在线文档 (飞书)**: [点击查看详细文档](https://sh6uqljbln.feishu.cn/wiki/F0tRwBQl4itZ6RkSgbtcBRv9nI6?from=from_copylink)

---

## 🏗 系统架构

本项目采用前后端分离的架构设计：

- **后端 (Backend)**: 基于 Python 的 **FastAPI** 框架，提供高性能的 RESTful API 服务，使用 **SQLAlchemy** 进行异步数据库操作。
- **前端 (Frontend)**: 基于 **Vue 3** 和 **Vite** 构建的单页应用 (SPA)，使用 **Element Plus** 组件库打造美观、响应式的用户界面。

## 🛠 技术栈

### 后端 (Server)
- **核心框架**: [FastAPI](https://fastapi.tiangolo.com/) (高性能 Python Web 框架)
- **数据库 ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) (Async IO 支持)
- **包管理**: [uv](https://github.com/astral-sh/uv) (极速 Python 包管理器)
- **认证安全**: OAuth2 + JWT (`python-jose`, `passlib`)
- **测试框架**: [pytest](https://docs.pytest.org/)

### 前端 (Web)
- **核心框架**: [Vue 3](https://vuejs.org/) (Composition API)
- **构建工具**: [Vite](https://vitejs.dev/)
- **UI 组件库**: [Element Plus](https://element-plus.org/)
- **状态管理**: [Pinia](https://pinia.vuejs.org/)
- **语言**: [TypeScript](https://www.typescriptlang.org/)

---

## ✨ 核心功能

### 1. 多角色权限管理
- **学生**: 浏览课程、选课/退课、查看课件、提交作业、查看成绩与反馈。
- **教师**: 创建/管理课程、上传课件、发布作业/考试、批改作业、管理选课名单、发布公告。
- **管理员**:系统级用户管理、全局公告发布、系统配置维护。

### 2. 课程体系
- **课程展现**: 丰富的课程详情页，支持富文本介绍。
- **章节管理**: 结构化的课程章节设计，支持课件（Slides）与视频链接。
- **选课系统**: 灵活的选课与退课机制，支持人数限制与审核（可选）。

### 3. 作业与考试
- **任务发布**: 支持发布普通作业和限时考试。
- **文件上传**: 集成文件上传功能，支持提交 PDF、图片等多种格式附件。
- **评分反馈**: 教师可在线预览提交内容，并在打分时提供详细的文字反馈。

### 4. 数据可视化与交互
- **仪表盘**: 为不同角色定制的首页仪表盘，展示待办事项、公告和统计数据。
- **成绩统计**: 可视化的成绩分布与趋势分析（开发中）。

---

## ⚡ 快速开始 (Quick Start)

### 1. 环境准备
确保你的本地环境已安装以下工具：
- **Python**: 3.13+
- **Node.js**: v18+
- **MySql**: 8.0+ (推荐) 或 SQLite
- **uv**: Python 包管理器 (`pip install uv`)

### 2. 后端启动 (Server)

```bash
cd server

# 1. 创建并激活虚拟环境
uv venv --python python3.13
.venv\Scripts\activate  # Windows PowerShell
# source .venv/bin/activate # Linux/macOS

# 2. 安装依赖
uv sync

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，修改 DATABASE_URL 为你的数据库连接串
# 示例: DATABASE_URL="mysql+aiomysql://root:password@localhost:3306/ustc_db"

# 4. 运行服务
uv run uvicorn app.main:app --reload
```

后端服务启动后，API 文档地址:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. 前端启动 (Web)

新建一个终端窗口：

```bash
cd web

# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

前端页面访问地址: `http://localhost:5173`

---

## 📂 项目目录概览

```
ustc-database-learning-platform/
├── server/                 # 后端代码目录
│   ├── app/                # 应用核心逻辑
│   │   ├── routers/        # API 路由
│   │   ├── models/         # 数据库模型
│   │   └── schemas/        # Pydantic 数据校验
│   ├── tests/              # 测试用例
│   ├── database_schema.sql # 数据库初始化脚本
│   └── pyproject.toml      # 后端依赖配置
├── web/                    # 前端代码目录
│   ├── src/
│   │   ├── views/          # 页面视图组件
│   │   ├── components/     # 公共组件
│   │   ├── stores/         # Pinia 状态管理
│   │   └── api/            # 接口请求封装
│   └── package.json        # 前端依赖配置
└── README.md               # 项目说明文档
```

## 🤝 贡献与许可
本项目为课程设计项目，欢迎提出 Issue 或 Pull Request 进行交流学习。
