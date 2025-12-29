import sys
import os
import asyncio
import logging

# 将当前目录添加到 Python 路径，以便能导入 app 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.email import email_service
import smtplib

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# *** 开启详细调试日志 ***
def set_debug_level():
    # 这里的 hack 是为了让 email_service 内部创建的 server 实例能打印日志
    # 但由于 email_service 每次发送都新建连接，我们需要在发送前打印提示
    print("[Debug] 已准备开启 SMTP 调试模式...")

def test_send_email():
    print("=" * 50)
    print("SMTP 邮件发送测试工具")
    print("=" * 50)

    # 1. 检查配置
    print(f"当前 SMTP 配置:")
    print(f"Host: {settings.SMTP_HOST}")
    print(f"Port: {settings.SMTP_PORT}")
    print(f"User: {settings.SMTP_USER}")
    print(f"Use TLS: {settings.SMTP_USE_TLS}")
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("\n[错误] SMTP_USER 或 SMTP_PASSWORD 未配置！")
        print("请在 app/core/config.py 中配置，或者在 .env 文件中设置。")
        print("也可以直接修改本脚本中的配置进行临时测试。")
        
        # 临时配置输入（可选）
        use_manual = input("\n是否现在手动输入 SMTP 配置进行测试？(y/n): ")
        if use_manual.lower() == 'y':
            settings.SMTP_HOST = input("SMTP Host (例如 smtp.qq.com): ") or "smtp.qq.com"
            settings.SMTP_PORT = int(input("SMTP Port (例如 465 或 587): ") or "465")
            settings.SMTP_USER = input("邮箱账号: ")
            settings.SMTP_PASSWORD = input("邮箱授权码/密码: ")
            settings.FROM_EMAIL = settings.SMTP_USER
            settings.FROM_NAME = "USTC Learning Platform Test"
            
            # 手动更新 email_service 的配置
            email_service.smtp_host = settings.SMTP_HOST
            email_service.smtp_port = settings.SMTP_PORT
            email_service.smtp_user = settings.SMTP_USER
            email_service.smtp_password = settings.SMTP_PASSWORD
            email_service.from_email = settings.FROM_EMAIL
            email_service.from_name = settings.FROM_NAME
            
            # 根据端口判断是否使用 TLS (通常 465 是 SSL, 587 是 TLS)
            if settings.SMTP_PORT == 465:
                settings.SMTP_USE_TLS = False # 使用 SSL
            else:
                settings.SMTP_USE_TLS = True
        else:
            return

    # 2.获取接收邮箱
    to_email = "2126015288@qq.com"

    # 3. 发送测试
    print(f"\n正在尝试发送邮件到 {to_email} ...")
    
    # 临时修改标题以避免被识别为垃圾邮件
    purpose = "学习平台系统测试" 
    
    print("提示：如果长时间卡住，可能是网络连接问题。")
    try:
        # 注意：smtplib 的 set_debuglevel 需要在连接对象上调用，
        # 但我们无法直接访问 email_service 内部的 server 对象。
        # 如果需要深层调试，可以临时修改 app/core/email.py，
        # 但通常如果报错会抛出异常。如果没有报错，说明服务器已经接收了请求。
        
        success = email_service.send_verification_code(to_email, "888888", purpose)
        if success:
            print("\n[成功] 邮件发送成功！请检查收件箱。")
        else:
            print("\n[失败] 邮件发送失败，请检查日志输出。")
    except Exception as e:
        print(f"\n[异常] 发送过程中发生错误: {e}")

if __name__ == "__main__":
    test_send_email()
