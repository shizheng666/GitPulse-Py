"""读取并校验项目运行配置。"""

from __future__ import annotations

import os

from dotenv import load_dotenv

from trending_monitor.models import AppConfig, SmtpConfig


REQUIRED_KEYS = (
    "TRENDING_URL",
    "FETCH_TIMEOUT",
    "TOP_N",
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "FROM_EMAIL",
    "TO_EMAIL",
)


def load_settings() -> AppConfig:
    """从环境变量中加载应用配置。

    配置说明：
    - ``TRENDING_URL``：必填，GitHub Trending 页面地址
    - ``FETCH_TIMEOUT``：可选，网络请求超时时间，默认 15 秒
    - ``TOP_N``：可选，邮件中最多展示多少个项目，默认 20
    - ``DATA_DIR``：可选，本地快照目录，默认 ``data``
    - ``SMTP_*`` / ``FROM_EMAIL`` / ``TO_EMAIL``：邮件发送必填配置
    """

    load_dotenv()

    missing = [key for key in REQUIRED_KEYS if not os.getenv(key)]
    if missing:
        raise ValueError(f"缺少必要配置：{', '.join(missing)}")

    data_dir = os.getenv("DATA_DIR", "data")
    use_tls = os.getenv("SMTP_USE_TLS", "true").strip().lower() not in {"0", "false", "no"}

    smtp_config = SmtpConfig(
        host=os.environ["SMTP_HOST"],
        port=int(os.environ["SMTP_PORT"]),
        username=os.environ["SMTP_USERNAME"],
        password=os.environ["SMTP_PASSWORD"],
        from_email=os.environ["FROM_EMAIL"],
        to_email=os.environ["TO_EMAIL"],
        use_tls=use_tls,
    )

    return AppConfig(
        trending_url=os.environ["TRENDING_URL"],
        fetch_timeout=int(os.environ["FETCH_TIMEOUT"]),
        top_n=int(os.environ["TOP_N"]),
        smtp=smtp_config,
        data_dir=data_dir,
    )
