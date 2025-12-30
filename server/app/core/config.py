from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "USTC Database Learning Platform"
    API_V1_STR: str = "/api/v1"
    
    # Database
    # 默认使用 SQLite，如果 .env 中配置了 DATABASE_URL 则使用 MySQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"
    
    # Security
    SECRET_KEY: str = "CHANGE_THIS_TO_A_SECURE_SECRET_KEY"  # 请在生产环境中修改
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email / SMTP Configuration
    SMTP_HOST: str = "smtp.gmail.com"  # 或使用 smtp.qq.com, smtp.163.com 等
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # 发件邮箱地址
    SMTP_PASSWORD: str = ""  # 邮箱授权码（不是邮箱密码）
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: str = ""  # 发件人邮箱（通常与 SMTP_USER 相同）
    FROM_NAME: str = "USTC数据库学习平台"
    
    # Development mode - skip actual email sending
    DEV_MODE: bool = True  # 开发模式：不实际发送邮件，直接返回验证码
    
    class Config:
        case_sensitive = True
        # 从 .env 文件读取配置
        env_file = os.path.join(BASE_DIR, ".env")
        env_file_encoding = 'utf-8'

settings = Settings()
