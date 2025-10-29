from venv import logger

from fastapi import BackgroundTasks, Form
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


fm = FastMail(conf)


# TODO 通知前端 邮件发送异常与否
def send_verify_code(
    background_tasks: BackgroundTasks,
    recipient: EmailStr,
    code: str,
):
    html_content = f"""
    <!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <!-- 一些客户端会参考这两个声明做暗黑模式适配 -->
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Bichon 验证码</title>
  </head>
  <body style="margin:0;padding:0;background:#f6f7fb;">
    <!-- 外层 100% 容器 -->
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background:#f6f7fb;">
      <tr>
        <td align="center" style="padding:24px;">
          <!-- 卡片容器：常用 600px -->
          <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="max-width:600px;background:#ffffff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.06);">
            <!-- 顶部横幅 -->
            <tr>
              <td align="left" style="padding:20px 24px;border-bottom:1px solid #eef0f4;">
                <div style="font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
                            font-size:24px;font-weight:700;color:#111827;letter-spacing:.3px;">
                  Bichon
                </div>
              </td>
            </tr>

            <!-- 正文 -->
            <tr>
              <td style="padding:24px;">
                <div style="font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
                            font-size:16px;line-height:1.7;color:#374151;">
                  <p style="margin:0 0 12px 0;">您好，</p>
                  <p style="margin:0 0 16px 0;">以下是您本次的验证码，请在 <strong>10 分钟</strong> 内使用：</p>

                  <!-- 验证码块 -->
                  <div style="margin:18px 0;padding:16px 20px;border:1px dashed #d1d5db;border-radius:10px;background:#f9fafb;
                              font-size:28px;font-weight:800;letter-spacing:4px;text-align:center;color:#111827;">
                    {code}
                  </div>
                </div>
              </td>
            </tr>

            <!-- 页脚 -->
            <tr>
              <td style="padding:12px 24px 20px 24px;border-top:1px solid #eef0f4;">
                <div style="font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
                            font-size:12px;line-height:1.6;color:#9ca3af;text-align:left;">
                  这是一封系统通知邮件，请勿直接回复。
                </div>
              </td>
            </tr>
          </table>

          <!-- 二级留白 -->
          <div style="height:8px;line-height:8px;font-size:8px;">&nbsp;</div>
        </td>
      </tr>
    </table>
  </body>
</html>

    """
    message = MessageSchema(
        subject="Your Verification Code",
        recipients=[recipient],
        body=html_content,
        subtype="html",
    )
    background_tasks.add_task(fm.send_message, message)


def send_invite_url(
    background_tasks: BackgroundTasks,
    recipient: EmailStr,
    invite_url: str,
):
    html_content = f"""
        <!doctype html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8">
        <meta name="color-scheme" content="light dark">
        <meta name="supported-color-schemes" content="light dark">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Bichon 邀请</title>
      </head>
      <body style="margin:0;padding:0;background:#f6f7fb;">
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background:#f6f7fb;">
          <tr>
            <td align="center" style="padding:24px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="max-width:600px;background:#ffffff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,0.06);">
                <tr>
                  <td align="left" style="padding:20px 24px;border-bottom:1px solid #eef0f4;">
                    <div style="font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
                                font-size:24px;font-weight:700;color:#111827;letter-spacing:.3px;">
                      Zetta
                    </div>
                  </td>
                </tr>

                <!-- 正文 -->
                <tr>
                  <td style="padding:24px;">
                    <div style="font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
                                font-size:16px;line-height:1.7;color:#374151;">
                      <p style="margin:0 0 12px 0;">您好，</p>
                      <p style="margin:0 0 16px 0;">以下是您本次的注册地址</p>
                      <div style="margin:18px 0;padding:16px 20px;border:1px dashed #d1d5db;border-radius:10px;background:#f9fafb;
                                  font-size:12px;font-weight:400;text-align:center;">
                        {invite_url}
                      </div>
                    </div>
                  </td>
                </tr>

                <!-- 页脚 -->
                <tr>
                  <td style="padding:12px 24px 20px 24px;border-top:1px solid #eef0f4;">
                    <div style="font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
                                font-size:12px;line-height:1.6;color:#9ca3af;text-align:left;">
                      这是一封系统通知邮件，请勿直接回复。
                    </div>
                  </td>
                </tr>
              </table>

              <!-- 二级留白 -->
              <div style="height:8px;line-height:8px;font-size:8px;">&nbsp;</div>
            </td>
          </tr>
        </table>
      </body>
    </html>

        """
    message = MessageSchema(
        subject="Your Verification Code",
        recipients=[recipient],
        body=html_content,
        subtype="html",
    )
    background_tasks.add_task(fm.send_message, message)
