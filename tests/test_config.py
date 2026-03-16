"""配置加载测试。"""

from __future__ import annotations

import pytest

from trending_monitor.config import load_settings


def test_load_settings_reads_env_values(monkeypatch) -> None:
    """配置加载器应能读取环境变量并转换为结构化配置。"""

    monkeypatch.setenv("TRENDING_URL", "https://github.com/trending")
    monkeypatch.setenv("FETCH_TIMEOUT", "20")
    monkeypatch.setenv("TOP_N", "10")
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USERNAME", "sender@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret-token")
    monkeypatch.setenv("FROM_EMAIL", "sender@example.com")
    monkeypatch.setenv("TO_EMAIL", "receiver@example.com")
    monkeypatch.setenv("DATA_DIR", "data")

    settings = load_settings()

    assert settings.trending_url == "https://github.com/trending"
    assert settings.fetch_timeout == 20
    assert settings.top_n == 10
    assert settings.data_dir == "data"
    assert settings.smtp.host == "smtp.example.com"
    assert settings.smtp.port == 587


def test_load_settings_raises_error_when_required_env_missing(monkeypatch) -> None:
    """缺失必要配置时应抛出中文错误，帮助快速定位问题。"""

    for key in (
        "TRENDING_URL",
        "FETCH_TIMEOUT",
        "TOP_N",
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "FROM_EMAIL",
        "TO_EMAIL",
        "DATA_DIR",
    ):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(ValueError, match="缺少必要配置"):
        load_settings()
