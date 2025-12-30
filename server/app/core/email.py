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
    def send_verification_code(self, to_email: str, code: str, purpose: str = "密码重置") -> bool:
        try:
            # 1. 准备邮件内容
            # 使用 MIMEMultipart 以支持 HTML，如果只想发纯文本可改为 MIMEText
            msg = MIMEMultipart('alternative')
            
            # 修正1：Subject 使用 Header 封装，防止乱码
            from email.header import Header
            subject = f'{settings.PROJECT_NAME} - {purpose}验证码'
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 修正2：From 头严格使用发送账号，避免被 163 拦截
            # 很多国内邮箱要求 From 必须和 login 的 user 完全一致
            sender = self.smtp_user
            msg['From'] = sender 
            msg['To'] = to_email

            # 邮件正文（保留 HTML 格式以维持美观，但在发送层参考了您的简单逻辑）
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        .container {{ padding: 20px; background-color: #f5f5f5; }}
        .box {{ background: white; padding: 20px; border-radius: 5px; }}
        .code {{ font-size: 24px; font-weight: bold; color: #409EFF; letter-spacing: 2px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="box">
            <h3>{purpose}</h3>
            <p>您的验证码是：</p>
            <p class="code">{code}</p>
            <p>10分钟内有效，过期请重新获取。</p>
            <p style="font-size: 12px; color: #999;">{settings.PROJECT_NAME} 系统邮件</p>
        </div>
    </div>
</body>
</html>
            """
            
            # 如果只想发纯文本：
            # msg.attach(MIMEText(f"您的验证码是：{code}", 'plain', 'utf-8'))
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            # 2. 发送邮件 (参考您的 sendEmail 函数逻辑)
            # 根据端口自动选择 SSL
            if self.smtp_port == 465:
                # 端口 465 强制使用 SSL
                smtp_obj = smtplib.SMTP_SSL(self.smtp_host, 465)
            else:
                # 其他端口（如 25, 587）使用普通 SMTP + STARTTLS
                smtp_obj = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if settings.SMTP_USE_TLS:
                    smtp_obj.starttls()

            smtp_obj.login(self.smtp_user, self.smtp_password)
            smtp_obj.sendmail(sender, [to_email], msg.as_string())
            smtp_obj.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False


# 创建全局实例
email_service = EmailService()
