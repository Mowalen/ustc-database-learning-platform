# 后端

## 快速开始

```bash
cd server
# 1) 创建虚拟环境（可指定解释器）
uv venv --python python3.13  # 或省略 --python 使用系统默认

# 2) 激活环境（根据 shell 选择下列其一）
source .venv/bin/activate        # bash/zsh
# 或
.venv\\Scripts\\activate         # Windows PowerShell/cmd

# 3) 安装依赖（基于 pyproject.toml/uv.lock）
uv sync

# 运行开发服务
uv run uvicorn main:app --reload
```

## 数据库配置

默认使用 MySQL 连接串（`mysql+aiomysql://root:password@localhost:3306/ustc_db`）。根据你的环境调整：

```bash
export DATABASE_URL="mysql+aiomysql://user:pass@localhost:3306/ustc_db"
```

其他驱动也可通过 `DATABASE_URL` 切换（例如 PostgreSQL `postgresql+asyncpg://user:pass@localhost:5432/dbname`）。
