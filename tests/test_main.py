"""主入口编排测试。"""

from __future__ import annotations

from trending_monitor.models import AppConfig, SmtpConfig, TrendingRepo
import main


def test_run_executes_full_pipeline(monkeypatch, tmp_path) -> None:
    """主流程应按顺序调用配置、抓取、解析、保存和发信。"""

    smtp_config = SmtpConfig(
        host="smtp.example.com",
        port=587,
        username="sender@example.com",
        password="secret",
        from_email="sender@example.com",
        to_email="receiver@example.com",
    )
    app_config = AppConfig(
        trending_url="https://github.com/trending",
        fetch_timeout=15,
        top_n=20,
        smtp=smtp_config,
        data_dir=str(tmp_path / "data"),
    )
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
        )
    ]
    calls: list[str] = []

    monkeypatch.setattr(main, "load_settings", lambda: app_config)
    monkeypatch.setattr(main, "fetch_trending_page", lambda url, timeout: calls.append("fetch") or "<html></html>")
    monkeypatch.setattr(main, "parse_trending", lambda html, base_url, limit: calls.append("parse") or items)
    monkeypatch.setattr(main, "save_snapshot", lambda repos, data_dir: calls.append("save") or str(tmp_path / "data.json"))
    monkeypatch.setattr(main, "build_email_html", lambda repos, fetch_date: calls.append("html") or "<html></html>")
    monkeypatch.setattr(main, "send_email", lambda subject, html, smtp: calls.append("send"))

    exit_code = main.run()

    assert exit_code == 0
    assert calls == ["fetch", "parse", "save", "html", "send"]
