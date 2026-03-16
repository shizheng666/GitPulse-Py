"""邮件正文拼装与发送逻辑。"""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

from trending_monitor.models import SmtpConfig, TrendingRepo


def build_email_html(items: list[TrendingRepo], fetch_date: str) -> str:
    """根据热门项目列表生成 HTML 邮件正文。"""

    rows: list[str] = []
    for item in items:
        # 这里按学习项目的可读性优先，使用简单卡片布局，避免邮件样式过于复杂。
        rows.append(
            f"""
            <tr>
              <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                <div style="font-size: 16px; font-weight: bold;">
                  <a href="{escape(item.repo_url)}" style="color: #2563eb; text-decoration: none;">
                    {escape(item.repo_name)}
                  </a>
                </div>
                <div style="margin: 8px 0; color: #374151;">{escape(item.description or "暂无描述")}</div>
                <div style="font-size: 13px; color: #6b7280;">
                  语言：{escape(item.language)} |
                  Stars：{item.stars} |
                  Forks：{item.forks} |
                  今日新增 Stars：{item.stars_today}
                </div>
              </td>
            </tr>
            """
        )

    body = "".join(rows) if rows else "<tr><td style='padding:12px;'>今日未抓取到热门项目。</td></tr>"

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; background: #f8fafc; padding: 24px;">
        <h2 style="color: #111827;">GitHub 今日热门项目日报 - {escape(fetch_date)}</h2>
        <table style="width: 100%; max-width: 900px; background: white; border-collapse: collapse;">
          {body}
        </table>
      </body>
    </html>
    """


def send_email(subject: str, html: str, smtp_config: SmtpConfig) -> None:
    """通过 SMTP 发送 HTML 邮件。"""

    # 邮件头和正文使用标准库构造，后续如需扩展附件也能平滑演进。
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = smtp_config.from_email
    message["To"] = smtp_config.to_email
    message.attach(MIMEText(html, "html", "utf-8"))

    try:
        # 465 通常表示隐式 SSL，需要直接建立加密连接；
        # 587 则更常见于普通 SMTP + STARTTLS 升级连接。
        smtp_client = smtplib.SMTP_SSL if smtp_config.port == 465 else smtplib.SMTP
        with smtp_client(smtp_config.host, smtp_config.port, timeout=30) as server:
            # 大多数邮箱服务使用授权码而不是登录密码。
            if smtp_config.port != 465 and smtp_config.use_tls:
                server.starttls()
            server.login(smtp_config.username, smtp_config.password)
            server.sendmail(
                smtp_config.from_email,
                [smtp_config.to_email],
                message.as_string(),
            )
    except smtplib.SMTPException as exc:
        raise RuntimeError(f"邮件发送失败，请检查 SMTP 配置或授权码：{exc}") from exc
    except OSError as exc:
        raise RuntimeError(f"无法连接到 SMTP 服务器：{exc}") from exc
