import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    def send_verification_code(self, to_email: str, code: str, purpose: str = "密码重置") -> bool:
        """
        发送验证码邮件
        
        Args:
            to_email: 收件人邮箱
            code: 验证码
            purpose: 验证码用途（如 "密码重置"、"邮箱验证" 等）
        
        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'{settings.PROJECT_NAME} - {purpose}验证码'
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = to_email

            # 邮件正文（纯文本版本）
            text_body = f"""
您好！

您正在进行{purpose}操作，验证码为：

{code}

验证码将在 10 分钟后失效，请尽快使用。

如果这不是您本人的操作，请忽略此邮件。

---
{settings.PROJECT_NAME}
"""

            # 邮件正文（HTML版本）
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: #f9f9f9;
            border-radius: 8px;
            padding: 30px;
            margin: 20px 0;
        }}
        .code-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
        }}
        .code {{
            font-size: 32px;
            font-weight: bold;
            letter-spacing: 8px;
            font-family: 'Courier New', monospace;
        }}
        .footer {{
            color: #999;
            font-size: 12px;
            margin-top: 30px;
            text-align: center;
        }}
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🔐 {purpose}验证码</h2>
        <p>您好！</p>
        <p>您正在进行<strong>{purpose}</strong>操作，请使用以下验证码完成验证：</p>
        
        <div class="code-box">
            <div class="code">{code}</div>
        </div>
        
        <div class="warning">
            ⏰ 验证码将在 <strong>10 分钟</strong>后失效，请尽快使用。
        </div>
        
        <p>如果这不是您本人的操作，请忽略此邮件。</p>
        
        <div class="footer">
            <p>{settings.PROJECT_NAME}</p>
            <p>此邮件由系统自动发送，请勿回复</p>
        </div>
    </div>
</body>
</html>
"""

            # 添加正文部分
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)

            # 发送邮件
            if settings.SMTP_USE_TLS:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Verification code email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False


# 创建全局实例
email_service = EmailService()
