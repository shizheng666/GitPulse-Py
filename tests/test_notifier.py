"""邮件正文生成与发送测试。"""

from __future__ import annotations

import smtplib

from trending_monitor.models import TrendingRepo
from trending_monitor.models import SmtpConfig
from trending_monitor.notifier import build_email_html, send_email


def test_build_email_html_contains_project_information() -> None:
    """邮件正文中应包含项目关键信息和可点击链接。"""

    items = [
        TrendingRepo(
            repo_name="openai/openai-python",
            repo_url="https://github.com/openai/openai-python",
            description="OpenAI Python SDK",
            language="Python",
            stars=12345,
            forks=1234,
            stars_today=567,
            fetched_at="2026-03-16T09:00:00+08:00",
        ),
        TrendingRepo(
            repo_name="vercel/next.js",
            repo_url="https://github.com/vercel/next.js",
            description="React framework for production",
            language="TypeScript",
            stars=98765,
            forks=10001,
            stars_today=89,
            fetched_at="2026-03-16T09:00:00+08:00",
        ),
    ]

    html = build_email_html(items, "2026-03-16")

    assert "GitHub 今日热门项目日报 - 2026-03-16" in html
    assert "openai/openai-python" in html
    assert "vercel/next.js" in html
    assert "https://github.com/openai/openai-python" in html
    assert "今日新增 Stars" in html
    assert "98765" in html


def test_send_email_uses_smtp_configuration(monkeypatch) -> None:
    """发送邮件时应按配置执行 TLS、登录和发信。"""

    actions: list[tuple[str, object]] = []

    class FakeSMTP:
        def __init__(self, host: str, port: int, timeout: int) -> None:
            actions.append(("init", (host, port, timeout)))

        def __enter__(self) -> "FakeSMTP":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def starttls(self) -> None:
            actions.append(("starttls", None))

        def login(self, username: str, password: str) -> None:
            actions.append(("login", (username, password)))

        def sendmail(self, from_email: str, to_emails: list[str], message: str) -> None:
            actions.append(("sendmail", (from_email, to_emails)))
            assert "Subject:" in message
            assert "Content-Type: text/html" in message

    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)

    smtp_config = SmtpConfig(
        host="smtp.example.com",
        port=587,
        username="sender@example.com",
        password="secret-token",
        from_email="sender@example.com",
        to_email="receiver@example.com",
        use_tls=True,
    )

    send_email("测试主题", "<html>body</html>", smtp_config)

    assert actions == [
        ("init", ("smtp.example.com", 587, 30)),
        ("starttls", None),
        ("login", ("sender@example.com", "secret-token")),
        ("sendmail", ("sender@example.com", ["receiver@example.com"])),
    ]
