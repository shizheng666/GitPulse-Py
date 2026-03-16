"""Trending 页面解析测试。"""

from __future__ import annotations

from pathlib import Path

from trending_monitor.parser import parse_trending


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "github_trending_sample.html"


def test_parse_trending_extracts_expected_fields() -> None:
    """解析器应能提取仓库名、链接和数值型字段。"""

    html = FIXTURE_PATH.read_text(encoding="utf-8")

    items = parse_trending(html, "https://github.com", limit=20)

    assert len(items) == 2
    assert items[0].repo_name == "openai/openai-python"
    assert items[0].repo_url == "https://github.com/openai/openai-python"
    assert items[0].description == "The official Python library for the OpenAI API."
    assert items[0].language == "Python"
    assert items[0].stars == 12345
    assert items[0].forks == 1234
    assert items[0].stars_today == 567


def test_parse_trending_handles_missing_optional_fields() -> None:
    """描述和语言缺失时应该回退到约定默认值。"""

    html = FIXTURE_PATH.read_text(encoding="utf-8")

    items = parse_trending(html, "https://github.com", limit=20)

    assert items[1].repo_name == "vercel/next.js"
    assert items[1].description == ""
    assert items[1].language == "Unknown"
    assert items[1].repo_url == "https://github.com/vercel/next.js"


def test_parse_trending_respects_limit() -> None:
    """limit 参数应该控制返回项目数量。"""

    html = FIXTURE_PATH.read_text(encoding="utf-8")

    items = parse_trending(html, "https://github.com", limit=1)

    assert len(items) == 1
