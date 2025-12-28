#!/usr/bin/env python3
"""
检查项目中仍在使用 SQLAlchemy 的文件

运行此脚本以查找需要迁移的文件
"""

import os
from pathlib import Path

# 要检查的目录
CHECK_DIRS = [
    "app/routers",
    "app/crud",
    "app/middleware"
]

# 要查找的 SQLAlchemy 特征字符串
SQLALCHEMY_PATTERNS = [
    "from sqlalchemy",
    "import sqlalchemy",
    "AsyncSession",
    "from app.db.session import",
    "from app.models.",
    "result.scalars()",
    "session.execute",
    "session.add",
    "session.commit",
    "relationship(",
    "Column(",
    "select(",
]

def check_file(filepath: Path) -> list[str]:
    """检查单个文件是否包含 SQLAlchemy 代码"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        found_patterns = []
        for pattern in SQLALCHEMY_PATTERNS:
            if pattern in content:
                found_patterns.append(pattern)
        
        return found_patterns
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def main():
    script_dir = Path(__file__).parent
    
    print("🔍 检查 SQLAlchemy 使用情况...\n")
    print("=" * 70)
    
    files_to_migrate = []
    
    for check_dir in CHECK_DIRS:
        dir_path = script_dir / check_dir
        
        if not dir_path.exists():
            print(f"⚠️  目录不存在: {check_dir}")
            continue
        
        print(f"\n📁 检查目录: {check_dir}")
        print("-" * 70)
        
        for py_file in dir_path.rglob("*.py"):
            if py_file.name == "__pycache__":
                continue
            
            patterns = check_file(py_file)
            
            if patterns:
                rel_path = py_file.relative_to(script_dir)
                files_to_migrate.append(str(rel_path))
                
                print(f"\n  ⚠️  {rel_path}")
                print(f"     发现 {len(patterns)} 个 SQLAlchemy 特征:")
                for pattern in patterns[:3]:  # 只显示前3个
                    print(f"       - {pattern}")
                if len(patterns) > 3:
                    print(f"       ... 还有 {len(patterns) - 3} 个")
            else:
                rel_path = py_file.relative_to(script_dir)
                print(f"  ✅ {rel_path}")
    
    print("\n" + "=" * 70)
    print(f"\n📊 统计:")
    print(f"   需要迁移的文件数: {len(files_to_migrate)}")
    
    if files_to_migrate:
        print("\n📝 需要迁移的文件列表:")
        for filepath in files_to_migrate:
            print(f"   - {filepath}")
        
        print("\n💡 提示:")
        print("   1. 参考 MIGRATION_GUIDE.md 了解迁移步骤")
        print("   2. 参考 app/routers/auth.py 作为迁移示例")
        print("   3. 所有 CRUD 文件已迁移完成，可直接使用")
    else:
        print("\n🎉 太棒了！所有文件都已迁移完成！")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
