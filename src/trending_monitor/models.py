"""项目中使用的数据模型定义。"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class TrendingRepo:
    """表示一个 GitHub 热门仓库的数据结构。"""

    repo_name: str
    repo_url: str
    description: str
    language: str
    stars: int
    forks: int
    stars_today: int
    fetched_at: str

    def to_dict(self) -> dict[str, str | int]:
        """将数据类转换为适合 JSON 序列化的字典。"""

        return asdict(self)


@dataclass(slots=True)
class SmtpConfig:
    """邮件发送所需的 SMTP 配置。"""

    host: str
    port: int
    username: str
    password: str
    from_email: str
    to_email: str
    use_tls: bool = True


@dataclass(slots=True)
class AppConfig:
    """应用运行时所需的全部配置。"""

    trending_url: str
    fetch_timeout: int
    top_n: int
    smtp: SmtpConfig
    data_dir: str

