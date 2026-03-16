"""GitHub Trending 页面解析逻辑。"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

from trending_monitor.link_utils import normalize_repo_url
from trending_monitor.models import TrendingRepo


WHITESPACE_RE = re.compile(r"\s+")
NUMBER_RE = re.compile(r"(\d[\d,]*)")


def _clean_text(text: str | None) -> str:
    """清洗文本中的多余空白，统一输出为单行文本。"""

    if not text:
        return ""
    return WHITESPACE_RE.sub(" ", text).strip()


def _extract_number(text: str | None) -> int:
    """从带说明文字的字符串中提取整数。

    示例：
    - ``1,234`` -> ``1234``
    - ``56 stars today`` -> ``56``
    """

    if not text:
        return 0

    match = NUMBER_RE.search(text)
    if not match:
        return 0
    return int(match.group(1).replace(",", ""))


def _extract_repo_name(title: str, repo_url: str) -> str:
    """将仓库名整理为 owner/repo 格式。

    GitHub Trending 页面标题有时会保留展示用大小写，因此这里优先使用链接路径，
    以保证仓库名和真实 URL 一致；标题文本只作为兜底来源。
    """

    path = urlparse(repo_url).path.strip("/")
    if path:
        return path
    return title.replace(" / ", "/").strip().replace(" ", "")


def _find_metric_links(article: Tag) -> list[Tag]:
    """提取项目卡片中的 stars 和 forks 链接。"""

    return article.select("div.f6 a[href*='stargazers'], div.f6 a[href*='forks']")


def parse_trending(html: str, base_url: str, limit: int) -> list[TrendingRepo]:
    """解析 GitHub Trending HTML，提取热门仓库核心信息。"""

    soup = BeautifulSoup(html, "html.parser")
    articles = soup.select("article.Box-row")
    fetched_at = datetime.now(timezone.utc).isoformat()

    items: list[TrendingRepo] = []
    for article in articles:
        if len(items) >= limit:
            break

        # 标题区域决定仓库名和仓库链接，这两个字段都属于关键字段。
        title_link = article.select_one("h2 a")
        if title_link is None:
            continue

        repo_title = _clean_text(title_link.get_text(" ", strip=True))
        repo_href = title_link.get("href", "")
        if not repo_title or not repo_href:
            continue

        try:
            repo_url = normalize_repo_url(base_url, repo_href)
        except ValueError:
            continue
        repo_name = _extract_repo_name(repo_title, repo_url)

        # 描述和语言都是可选字段，页面缺失时按默认值处理即可。
        description_node = article.select_one("p")
        language_node = article.select_one("span[itemprop='programmingLanguage']")
        description = _clean_text(description_node.get_text(" ", strip=True) if description_node else "")
        language = _clean_text(language_node.get_text(" ", strip=True) if language_node else "") or "Unknown"

        metric_links = _find_metric_links(article)
        stars = _extract_number(metric_links[0].get_text(" ", strip=True) if len(metric_links) > 0 else "")
        forks = _extract_number(metric_links[1].get_text(" ", strip=True) if len(metric_links) > 1 else "")

        # “今日新增 stars” 在卡片底部说明文字中，适合用正则从整段文本里提取数字。
        stars_today_node = article.select_one("span.float-sm-right")
        stars_today = _extract_number(
            stars_today_node.get_text(" ", strip=True) if stars_today_node else ""
        )

        items.append(
            TrendingRepo(
                repo_name=repo_name,
                repo_url=repo_url,
                description=description,
                language=language,
                stars=stars,
                forks=forks,
                stars_today=stars_today,
                fetched_at=fetched_at,
            )
        )

    return items
